from __future__ import annotations

import math
import queue
import re
import threading
import time
from typing import Any, Callable

from Logger import Logger
from Models.ComModel import ComModel
from Models.SettingModel import SettingModel

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None


def _format_command_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return format(value, ".15g")
    return str(value)


def _csharp_divide(numerator: float, denominator: float) -> float:
    numerator = float(numerator)
    denominator = float(denominator)
    if denominator == 0:
        if numerator == 0:
            return math.nan
        return math.copysign(math.inf, numerator)
    return numerator / denominator


def _csharp_floor_round(value: float) -> float:
    if math.isfinite(value):
        return round(math.floor(value), 0)
    return value


def _clamp(value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if math.isnan(value):
        return value
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


class ComViewModel:
    def __init__(self, sm: SettingModel, message_handler: Callable[[str], None] | None = None) -> None:
        self.PropertyChanged: list[Callable[[Any, str], None]] = []
        self.OnCommandSent: list[Callable[[str], None]] = []
        self.OnResponseReceived: list[Callable[[str], None]] = []

        self.serialPort: serial.Serial | None = None if serial is not None else None
        self.cancellationTokenSource: threading.Event | None = None

        self.linesToSend: queue.Queue[str] = queue.Queue()
        self.uiReceivedQueue: queue.Queue[str] = queue.Queue()
        self.uiSentQueue: queue.Queue[str] = queue.Queue()

        self.message_handler = message_handler or self._default_message_handler
        self.last_connect_error: str | None = None
        self.active_baudrate: int | None = None
        self._startup_messages: list[str] = []

        self._Setting = sm
        self._comModel = ComModel()

        self.isWinderAuto = False
        self.isSpoolerAuto = False
        self.isPullerAuto = False

        self.AugerRPM = 0.0
        self.SpoolerRPM = 0.0
        self.WinderRPM = 0.0
        self.PullerRPM = 0.0

        self._threads: list[threading.Thread] = []

    @property
    def Setting(self) -> SettingModel:
        return self._Setting

    @Setting.setter
    def Setting(self, value: SettingModel) -> None:
        self._Setting = value
        self.OnPropertyChanged("Setting")

    @property
    def comModel(self) -> ComModel:
        return self._comModel

    @comModel.setter
    def comModel(self, value: ComModel) -> None:
        self._comModel = value
        self.OnPropertyChanged("comModel")

    def add_OnCommandSent(self, callback: Callable[[str], None]) -> None:
        self.OnCommandSent.append(callback)

    def add_OnResponseReceived(self, callback: Callable[[str], None]) -> None:
        self.OnResponseReceived.append(callback)

    def ComChecks(self) -> None:
        if list_ports is None:
            self.comModel.Ports = []
            return
        ports = list(list_ports.comports())
        self.comModel.Ports = [port.device for port in ports]
        self.comModel.selectedPort = self._choose_port(ports, self.comModel.selectedPort)

    def SetInitialConnectState(self) -> None:
        self.comModel.OpRun = False
        self.comModel.Ack = 0
        self.linesToSend = queue.Queue()
        self.comModel.printerConnected = True
        self.comModel.Temp1On = False
        self.comModel.Temp2On = False
        self.comModel.Temp3On = False
        self.comModel.Temp4On = False

        self.SendCommand(self.Setting.commands.TempRead, "5")

    def ConnectCom(self) -> bool:
        if self.comModel.selectedPort is None:
            self.comModel.printerConnected = False
            self.message_handler("Select a com port")
            return False

        if not self.ConnectBoard():
            self.comModel.printerConnected = False
            self.serialPort = None
            detail = f": {self.last_connect_error}" if self.last_connect_error else ""
            self.message_handler(f"Printer failed to connect to {self.comModel.selectedPort}{detail}")
            return False

        self.StartCommunication()
        return True

    def ConnectBoard(self) -> bool:
        if serial is None:
            self.last_connect_error = "pyserial is not installed"
            return False

        self.last_connect_error = None
        self._startup_messages = []
        for baudrate in self._candidate_baudrates():
            try:
                port = serial.Serial(
                    port=self.comModel.selectedPort,
                    baudrate=baudrate,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=0.2,
                    write_timeout=0.5,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False,
                )
                port.dtr = True
                port.rts = True

                startup_messages = self._probe_serial_port(port)
                if startup_messages:
                    self.serialPort = port
                    self.active_baudrate = baudrate
                    self._startup_messages = startup_messages
                    self.message_handler(f"Connected to {self.comModel.selectedPort} at {baudrate} baud")
                    return True

                port.close()
            except OSError as ex:
                self.last_connect_error = str(ex)
                return False
            except PermissionError as ex:
                self.last_connect_error = str(ex)
                return False
            except Exception as ex:
                self.last_connect_error = str(ex)
                continue

        self.active_baudrate = None
        self.last_connect_error = self.last_connect_error or "No readable response received on common baud rates"
        return False

    def ComClose(self) -> bool:
        self.OpDisrupt()
        self.comModel.printerConnected = False

        if self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            self.cancellationTokenSource.set()

        if self.serialPort is not None and self.serialPort.is_open:
            self.serialPort.close()
            self.serialPort = None
            return False

        return True

    def EmergencyStop(self) -> None:
        self.OpDisrupt()
        time.sleep(1.0)

    def StartCommunication(self) -> None:
        self.comModel.OpRun = False
        self.comModel.isTuning = False

        self.cancellationTokenSource = threading.Event()
        self._threads = []

        serialReceiverThread = threading.Thread(target=self.SerialReceiver, name="SerialReceiver", daemon=True)
        serialReceiverThread.start()
        self._threads.append(serialReceiverThread)

        self._start_background(self.UICommandReceivedUpdateTask, "UICommandReceivedUpdateTask")
        self._start_background(self.SerialSender, "SerialSender")
        self._start_background(self.UICommandSentUpdateTask, "UICommandSentUpdateTask")

        for line in self._startup_messages:
            self._queue_received_line(line)
        self._startup_messages = []

    def SerialReceiver(self) -> None:
        buffer: list[str] = []
        last_data_time = 0.0

        while self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            try:
                if self.serialPort is not None and self.serialPort.in_waiting > 0:
                    data = self.serialPort.read(self.serialPort.in_waiting).decode(errors="ignore")
                    last_data_time = time.monotonic()
                    for ch in data:
                        if ch in ("\r", "\n"):
                            line = "".join(buffer).strip()
                            buffer.clear()

                            if len(line) > 1:
                                self._queue_received_line(line)
                        else:
                            buffer.append(ch)
                elif buffer and last_data_time and (time.monotonic() - last_data_time) > 0.2:
                    line = "".join(buffer).strip()
                    buffer.clear()
                    last_data_time = 0.0
                    if len(line) > 1:
                        self._queue_received_line(line)
                else:
                    time.sleep(0.005)
            except Exception:
                self.ComClose()
                break

    def UICommandReceivedUpdateTask(self) -> None:
        while self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            try:
                response = self.uiReceivedQueue.get_nowait()
            except queue.Empty:
                time.sleep(0.005)
                continue

            if "AUGER ERROR" in response:
                self.comModel.printerConnected = False
            elif "PID Autotune finished!" in response:
                self._start_background(self.SetPID, "SetPID")
            elif "Printer halted" in response:
                self.comModel.printerConnected = False
                self.message_handler(
                    "Connect to machine again.\n"
                    "Plug out and Plug in the power of the machine and restart the software again if it happens again.\n"
                    "If issue persists contact the team"
                )
            elif "Filament dia" in response:
                self.Setting.values.ReadFDia = float(response.split(":")[-1].strip())
                self.Setting.values.CurrFDia.append(self.Setting.values.ReadFDia)
                if self.isPullerAuto and self.comModel.OpRun:
                    if len(self.Setting.values.CurrFDia) > self.Setting.values.PIDInterval:
                        self.SetNewPuller()
            elif "Kp:" in response:
                self._start_background(lambda st=response: self.GetPID(st), "GetPID")
            elif "T:" in response or "T1:" in response:
                self._start_background(lambda st=response: self.GetTemp(st), "GetTemp")

            self._fire_response_received(response)
            time.sleep(0.005)

    def SerialSender(self) -> None:
        stringBuilder: list[str] = []
        _ = stringBuilder

        while self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            try:
                command = self.linesToSend.get_nowait()
            except queue.Empty:
                time.sleep(0.005)
                continue

            try:
                self.Send(command)
                time.sleep(0.01)
            except Exception:
                self.ComClose()
                break

    def UICommandSentUpdateTask(self) -> None:
        while self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            try:
                command = self.uiSentQueue.get_nowait()
            except queue.Empty:
                time.sleep(0.02)
                continue

            self._fire_command_sent(command)
            time.sleep(0.02)

    def StartOp(self) -> None:
        if self.serialPort is None or not self.serialPort.is_open:
            return

        self.comModel.OpRun = True
        self._start_background(self.SerialOpThread, "SerialOpThread")

    def SerialOpThread(self) -> None:
        j = 0
        i = 0
        wc = 1
        self.SendCommand(self.Setting.commands.Winder, "600")
        time.sleep(1.0)
        self.Send(self.Setting.commands.OpPreset)
        time.sleep(1.0)

        while self.comModel.Ack > 0:
            time.sleep(1.0)

        self.SendCommand(self.Setting.commands.WinderMove, _format_command_value(self.Setting.values.WinderStart))
        self.SendCommand(self.Setting.commands.WinderSetPos, "0")
        self.SendCommand(self.Setting.commands.Winder, _format_command_value(self.WinderRPM))

        while self.comModel.OpRun and self.cancellationTokenSource is not None and not self.cancellationTokenSource.is_set():
            try:
                if i >= self.Setting.values.CalcWinder:
                    wc = -wc
                    i = 0
                    j += 1
                    if j >= 2:
                        self.Setting.values.SpoolerID = self.Setting.values.SpoolerID + (2 * self.Setting.values.FDia)
                        j = 0
                        if self.isSpoolerAuto:
                            self.MotorControl("Spooler")
                i += 1

                self.ParseSend(self.Setting.commands.OpMotion, f"{wc}")
                self.Send(self.Setting.commands.FRead)
                if self.comModel.isLog:
                    Logger.Log(
                        f"FilamentDia : {self.Setting.values.ReadFDia}, "
                        f"AugerRPM : {self.AugerRPM}, PullerRPM : {self.PullerRPM}, "
                        f"SpoolerRPM : {self.SpoolerRPM}, WinderRPM : {self.WinderRPM}, "
                        f"T1 : {self.comModel.Temp1}, T2 : {self.comModel.Temp2}, "
                        f"T3 : {self.comModel.Temp3}, T4 : {self.comModel.Temp4}"
                    )
                time.sleep(self.Setting.values.OpDelay / 1000.0)
            except Exception:
                self.OpDisrupt()
                break

    def StopOp(self) -> None:
        self.OpDisrupt()

    def OpDisrupt(self) -> None:
        self.comModel.OpRun = False
        self.comModel.Ack = 0
        self.linesToSend = queue.Queue()

        self.SendCommand(self.Setting.commands.StopMotion)

    def Printgaps(self, input_value: str) -> str:
        if ";" in input_value:
            input_value = input_value.replace(";", "")
        result = re.sub(r"\s+", " ", input_value)
        return result.strip()

    def RemoveExcessiveGaps(self, input_value: str) -> str:
        if ";" in input_value:
            input_value = input_value.replace(";", "")
        result = re.sub(r"\s+", " ", input_value)
        result = result.upper()
        result = result.strip()
        result += ";"
        return result

    @staticmethod
    def ExtractValue(input_value: str, variable: str) -> float:
        pattern = re.escape(variable) + r"(-?\d+(?:\.\d+)?|-?\.\d+)"
        if ":" in input_value:
            pattern = re.escape(variable) + r":(-?\d+(?:\.\d+)?|-?\.\d+)"
        if "=" in input_value:
            pattern = re.escape(variable) + r"=(-?\d+(?:\.\d+)?|-?\.\d+)"

        match = re.search(pattern, input_value)
        if match:
            return round(float(match.group(1)), 2)
        return 0.0

    @staticmethod
    def ExtractPID(input_value: str, variable: str) -> float:
        pattern = re.escape(variable) + r"\s*[:=]?\s*(-?\d+(?:\.\d+)?|-?\.\d+)"
        match = re.search(pattern, input_value, flags=re.IGNORECASE)
        if match:
            return round(float(match.group(1)), 2)
        return 0.0

    def GetPID(self, st: str) -> None:
        self.Setting.values.TuningP = self.ExtractPID(st, "Kp")
        self.Setting.values.TuningI = self.ExtractPID(st, "Ki")
        self.Setting.values.TuningD = self.ExtractPID(st, "Kd")

    def GetTemp(self, st: str) -> None:
        self.comModel.Temp1 = self.ExtractValue(st, self.Setting.commands.Temp1Text) if f"{self.Setting.commands.Temp1Text}:" in st else -15
        self.comModel.Temp2 = self.ExtractValue(st, self.Setting.commands.Temp2Text) if f"{self.Setting.commands.Temp2Text}:" in st else -15
        self.comModel.Temp3 = self.ExtractValue(st, self.Setting.commands.Temp3Text) if f"{self.Setting.commands.Temp3Text}:" in st else -15
        self.comModel.Temp4 = self.ExtractValue(st, self.Setting.commands.Temp4Text) if f"{self.Setting.commands.Temp4Text}:" in st else -15

        if self.comModel.Temp1 == -15 and self.comModel.Temp1On:
            self.TempOff("1")
        if self.comModel.Temp2 == -15 and self.comModel.Temp2On:
            self.TempOff("2")
        if self.comModel.Temp3 == -15 and self.comModel.Temp3On:
            self.TempOff("3")
        if self.comModel.Temp4 == -15 and self.comModel.Temp4On:
            self.TempOff("4")

    def StartTuning(self) -> None:
        self.AllTempOff()
        e = {
            "1": -1,
            "2": 0,
            "3": -2,
            "4": 1,
        }[self.comModel.CurrT]
        self.SendCommand(f"M303 E{e} C{self.Setting.values.TuningCycles} S{self.Setting.values.TuningTemp}")
        self.comModel.isTuning = True

    def SetPID(self) -> None:
        c = {
            "1": "M304 ",
            "2": "M301 ",
            "3": "M309 ",
            "4": "M301 ",
        }[self.comModel.CurrT]
        self.SendCommand(
            c
            + "P"
            + _format_command_value(self.Setting.values.TuningP)
            + " I"
            + _format_command_value(self.Setting.values.TuningI)
            + " D"
            + _format_command_value(self.Setting.values.TuningD)
        )
        self.SendCommand("M500")
        self.comModel.isTuning = False
        self.message_handler(f"Pid Tuning is saved for T{self.comModel.CurrT}")

    def TempOn(self, tag: str) -> None:
        if tag == "1":
            self.SendCommand(self.Setting.commands.Temp1On, _format_command_value(self.comModel.SetTemp1))
            self.comModel.Temp1On = True
        elif tag == "2":
            self.SendCommand(self.Setting.commands.Temp2On, _format_command_value(self.comModel.SetTemp2))
            self.comModel.Temp2On = True
        elif tag == "3":
            self.SendCommand(self.Setting.commands.Temp3On, _format_command_value(self.comModel.SetTemp3))
            self.comModel.Temp3On = True
        elif tag == "4":
            self.SendCommand(self.Setting.commands.Temp4On, _format_command_value(self.comModel.SetTemp4))
            self.comModel.Temp4On = True

    def TempOff(self, tag: str) -> None:
        if tag == "1":
            self.comModel.Temp1On = False
            self.SendCommand(self.Setting.commands.Temp1Off)
        elif tag == "2":
            self.comModel.Temp2On = False
            self.SendCommand(self.Setting.commands.Temp2Off)
        elif tag == "3":
            self.comModel.Temp3On = False
            self.SendCommand(self.Setting.commands.Temp3Off)
        elif tag == "4":
            self.comModel.Temp4On = False
            self.SendCommand(self.Setting.commands.Temp4Off)

    def AllTempOff(self) -> None:
        if self.comModel.Temp1On:
            self.TempOff("1")
        if self.comModel.Temp2On:
            self.TempOff("2")
        if self.comModel.Temp3On:
            self.TempOff("3")
        if self.comModel.Temp4On:
            self.TempOff("4")

    def MotorControl(self, motor: str = "") -> None:
        if motor == "Auger":
            self.AugerRPM = round(self.Setting.values.Auger * self.Setting.values.Spmm / 60, 2)
            self.SendCommand(self.Setting.commands.Auger, _format_command_value(self.AugerRPM))
        elif motor == "Winder":
            self.WinderRPM = round(self.Setting.values.Winder, 2)
            calc_value = _csharp_divide(self.Setting.values.WinderSpmm * self.Setting.values.WinderMax, self.WinderRPM)
            self.Setting.values.CalcWinder = _csharp_floor_round(calc_value)
            self.SendCommand(self.Setting.commands.Winder, _format_command_value(self.WinderRPM))
        elif motor == "Spooler":
            s = _csharp_divide(self.Setting.values.Puller * self.Setting.values.PullerDia, self.Setting.values.SpoolerID)
            self.SpoolerRPM = round(s * self.Setting.values.SpoolerSpmm / 60, 2)
            self.SendCommand(self.Setting.commands.Spooler, _format_command_value(self.SpoolerRPM))
            if self.isWinderAuto:
                self.WinderRPM = round(self.SpoolerRPM * self.Setting.values.WinderPitch, 2)
                calc_value = _csharp_divide(self.Setting.values.WinderSpmm * self.Setting.values.WinderMax, self.WinderRPM)
                self.Setting.values.CalcWinder = _csharp_floor_round(calc_value)
                self.SendCommand(self.Setting.commands.Winder, _format_command_value(self.WinderRPM))
        elif motor == "Spool":
            self.SpoolerRPM = round(self.Setting.values.Spooler * self.Setting.values.SpoolerSpmm / 60, 2)
            self.SendCommand(self.Setting.commands.Spooler, _format_command_value(self.SpoolerRPM))
            if self.isWinderAuto:
                self.WinderRPM = round(self.SpoolerRPM * self.Setting.values.WinderPitch, 2)
                calc_value = _csharp_divide(self.Setting.values.WinderSpmm * self.Setting.values.WinderMax, self.WinderRPM)
                self.Setting.values.CalcWinder = _csharp_floor_round(calc_value)
                self.SendCommand(self.Setting.commands.Winder, _format_command_value(self.WinderRPM))
        else:
            self.PullerRPM = round(self.Setting.values.Puller * self.Setting.values.Spmm / 60, 2)
            self.SendCommand(self.Setting.commands.Puller, _format_command_value(self.PullerRPM))
            if self.isSpoolerAuto:
                self.MotorControl("Spooler")

    def FanControl(self, isOn: bool, fan: int = 0) -> None:
        intensity = 0.0
        if fan == 1:
            if isOn:
                self.SendCommand(self.Setting.commands.Fan1)
                return
            intensity = self.Setting.values.Fan1 * 2.55
            self.SendCommand(self.Setting.commands.Fan1, _format_command_value(round(intensity, 1)))
        elif fan == 2:
            if isOn:
                self.SendCommand(self.Setting.commands.Fan2)
                return
            intensity = self.Setting.values.Fan2 * 2.55
            self.SendCommand(self.Setting.commands.Fan2, _format_command_value(round(intensity, 1)))
        elif fan == 3:
            if isOn:
                self.SendCommand(self.Setting.commands.Fan3)
                return
            intensity = self.Setting.values.Fan3 * 2.55
            self.SendCommand(self.Setting.commands.Fan3, _format_command_value(round(intensity, 1)))

    def CustomSends(self, command: str) -> None:
        if self.serialPort is not None and self.serialPort.is_open:
            self.SendCommand(command)

    def ParseCommand(self, command: str, value: str | float | int = "0") -> None:
        if len(command) < 2:
            return
        command = self.RemoveExcessiveGaps(command)
        if "{}" in command:
            command = command.replace("{}", _format_command_value(value))
        self.linesToSend.put(command)

    def SendCommand(self, command: str | None, value: str | float | int = "0") -> None:
        if command is None:
            return
        parts = command.split(",")
        if len(parts) == 1:
            self.ParseCommand(command, value)
        else:
            for part in parts:
                self.ParseCommand(part, value)

    def ParseSend(self, command: str, value: str | float | int = "0") -> None:
        if "{}" in command:
            command = command.replace("{}", _format_command_value(value))
        self.Send(command)

    def Send(self, command: str | None) -> None:
        if self.serialPort is None or command is None:
            return
        self.serialPort.write((command + "\n").encode("utf-8"))
        self.comModel.Ack += 1
        self.uiSentQueue.put(command)

    def SetNewPuller(self) -> None:
        filament_control = self.Setting.values.Puller
        pid_input = sum(self.Setting.values.CurrFDia) / len(self.Setting.values.CurrFDia) if len(self.Setting.values.CurrFDia) > 0 else 0
        pid_error_fwidth = self.Setting.values.FDia - pid_input
        self.Setting.values.CurrFDia.clear()

        p = filament_control - self.Setting.values.PullerP * pid_error_fwidth

        if (filament_control < self.Setting.values.MaxPID and pid_error_fwidth < 0) or (
            filament_control > self.Setting.values.MinPID and pid_error_fwidth > 0
        ):
            self.Setting.values.dia_iState_fwidth += pid_error_fwidth * self.Setting.values.puller_increment
            self.Setting.values.dia_iState_fwidth = _clamp(
                self.Setting.values.dia_iState_fwidth,
                -self.Setting.values.IntegratorWindPID,
                self.Setting.values.IntegratorWindPID,
            )

        i = self.Setting.values.PullerI * self.Setting.values.dia_iState_fwidth

        d = (
            _csharp_divide(self.Setting.values.PullerD, self.Setting.values.puller_increment)
            * (pid_input - self.Setting.values.LastFDia)
        ) * self.Setting.values.K2 + (self.Setting.values.K1 * self.Setting.values.LastPullerD)
        self.Setting.values.LastPullerD = d
        self.Setting.values.LastFDia = pid_input

        filament_control = p - i + d
        filament_control = _clamp(filament_control, self.Setting.values.MinPID, self.Setting.values.MaxPID)

        self.Setting.values.Puller = filament_control
        self.MotorControl()

    def OnPropertyChanged(self, property_name: str) -> None:
        for callback in list(self.PropertyChanged):
            callback(self, property_name)

    def _fire_command_sent(self, command: str) -> None:
        for callback in list(self.OnCommandSent):
            callback(command)

    def _fire_response_received(self, response: str) -> None:
        for callback in list(self.OnResponseReceived):
            callback(response)

    def _start_background(self, target: Callable[[], None], name: str) -> None:
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        self._threads.append(thread)

    def _queue_received_line(self, line: str) -> None:
        if "ok" in line.lower() and self.comModel.Ack > 0:
            self.comModel.Ack -= 1
        self.uiReceivedQueue.put(line)

    @staticmethod
    def _candidate_baudrates() -> tuple[int, ...]:
        return (250000, 115200, 230400, 57600, 9600)

    def _probe_serial_port(self, port: Any) -> list[str]:
        messages: list[str] = []
        commands = ("", "M115", "M105", "M155 S1")

        time.sleep(2.5)
        port.reset_input_buffer()
        port.reset_output_buffer()

        for command in commands:
            if command:
                port.write((command + "\n").encode("utf-8"))
                port.flush()
            else:
                port.write(b"\n")
                port.flush()

            messages.extend(self._read_probe_lines(port, duration=1.2))
            if messages:
                break

        return messages

    def _read_probe_lines(self, port: Any, duration: float) -> list[str]:
        end_time = time.monotonic() + duration
        buffer = ""
        lines: list[str] = []

        while time.monotonic() < end_time:
            chunk = port.read(port.in_waiting or 1)
            if not chunk:
                time.sleep(0.05)
                continue

            buffer += chunk.decode("utf-8", errors="ignore")
            normalized = buffer.replace("\r", "\n")
            parts = normalized.split("\n")
            buffer = parts.pop() if parts else ""

            for part in parts:
                line = part.strip()
                if line:
                    lines.append(line)

        trailing = buffer.strip()
        if trailing:
            lines.append(trailing)

        return [line for line in lines if self._looks_like_device_output(line)]

    @staticmethod
    def _looks_like_device_output(line: str) -> bool:
        lowered = line.lower()
        indicators = ("ok", "error", "echo", "t:", "t0:", "t1:", "b:", "firmware", "marlin", "filament dia")
        return any(indicator in lowered for indicator in indicators)

    @staticmethod
    def _choose_port(ports: list[Any], current_port: str | None = None) -> str | None:
        if current_port and any(getattr(port, "device", None) == current_port for port in ports):
            return current_port
        if not ports:
            return None

        def port_score(port: Any) -> int:
            text = f"{getattr(port, 'device', '')} {getattr(port, 'description', '')} {getattr(port, 'hwid', '')}".lower()
            keywords = ("usb", "serial", "uart", "ch340", "cp210", "ftdi", "arduino", "esp")
            return sum(1 for keyword in keywords if keyword in text)

        return max(ports, key=port_score).device

    @staticmethod
    def _default_message_handler(message: str) -> None:
        print(message)
