from __future__ import annotations

from typing import Any, Callable

try:
    from serial.tools import list_ports
except ImportError:
    list_ports = None


class ComModel:
    def __init__(self) -> None:
        self.PropertyChanged: list[Callable[[Any, str], None]] = []

        self._Ports: list[str] = []
        self._selectedPort: str | None = None
        self._printerConnected: bool = False
        self._Ack: int = 0
        self._OpRun: bool = False
        self._isLog: bool = False

        self._SetTemp1: float = 200
        self._SetTemp2: float = 200
        self._SetTemp3: float = 200
        self._SetTemp4: float = 200

        self._Temp1: float = -15
        self._Temp2: float = -15
        self._Temp3: float = -15
        self._Temp4: float = -15

        self._Temp1On: bool = False
        self._Temp2On: bool = False
        self._Temp3On: bool = False
        self._Temp4On: bool = False

        self._CurrT: str = "1"
        self._isTuning: bool = False

        self.isTuning = False
        ports, selected_port = self._get_available_ports()
        self.Ports = ports
        if selected_port is not None:
            self.selectedPort = selected_port

    def _get_available_ports(self) -> tuple[list[str], str | None]:
        if list_ports is None:
            return [], None

        ports = list(list_ports.comports())
        port_names = [port.device for port in ports]
        selected_port = self._pick_default_port(ports)
        return port_names, selected_port

    @staticmethod
    def _pick_default_port(ports: list[Any]) -> str | None:
        if not ports:
            return None

        def port_score(port: Any) -> int:
            text = f"{getattr(port, 'device', '')} {getattr(port, 'description', '')} {getattr(port, 'hwid', '')}".lower()
            keywords = ("usb", "serial", "uart", "ch340", "cp210", "ftdi", "arduino", "esp")
            return sum(1 for keyword in keywords if keyword in text)

        return max(ports, key=port_score).device

    @property
    def Ports(self) -> list[str]:
        return self._Ports

    @Ports.setter
    def Ports(self, value: list[str] | None) -> None:
        self._Ports = list(value or [])
        self.OnPropertyChanged("Ports")

    @property
    def selectedPort(self) -> str | None:
        return self._selectedPort

    @selectedPort.setter
    def selectedPort(self, value: str | None) -> None:
        self._selectedPort = value
        self.OnPropertyChanged("selectedPort")

    @property
    def printerConnected(self) -> bool:
        return self._printerConnected

    @printerConnected.setter
    def printerConnected(self, value: bool) -> None:
        self._printerConnected = bool(value)
        self.OnPropertyChanged("printerConnected")

    @property
    def Ack(self) -> int:
        return self._Ack

    @Ack.setter
    def Ack(self, value: int) -> None:
        self._Ack = int(value)
        self.OnPropertyChanged("Ack")

    @property
    def OpRun(self) -> bool:
        return self._OpRun

    @OpRun.setter
    def OpRun(self, value: bool) -> None:
        self._OpRun = bool(value)
        self.OnPropertyChanged("OpRun")

    @property
    def isLog(self) -> bool:
        return self._isLog

    @isLog.setter
    def isLog(self, value: bool) -> None:
        self._isLog = bool(value)
        self.OnPropertyChanged("isLog")

    @property
    def SetTemp1(self) -> float:
        return self._SetTemp1

    @SetTemp1.setter
    def SetTemp1(self, value: float) -> None:
        self._SetTemp1 = float(value)
        self.OnPropertyChanged("SetTemp1")

    @property
    def SetTemp2(self) -> float:
        return self._SetTemp2

    @SetTemp2.setter
    def SetTemp2(self, value: float) -> None:
        self._SetTemp2 = float(value)
        self.OnPropertyChanged("SetTemp2")

    @property
    def SetTemp3(self) -> float:
        return self._SetTemp3

    @SetTemp3.setter
    def SetTemp3(self, value: float) -> None:
        self._SetTemp3 = float(value)
        self.OnPropertyChanged("SetTemp3")

    @property
    def SetTemp4(self) -> float:
        return self._SetTemp4

    @SetTemp4.setter
    def SetTemp4(self, value: float) -> None:
        self._SetTemp4 = float(value)
        self.OnPropertyChanged("SetTemp4")

    @property
    def Temp1(self) -> float:
        return self._Temp1

    @Temp1.setter
    def Temp1(self, value: float) -> None:
        self._Temp1 = round(float(value), 2)
        self.OnPropertyChanged("Temp1")

    @property
    def Temp2(self) -> float:
        return self._Temp2

    @Temp2.setter
    def Temp2(self, value: float) -> None:
        self._Temp2 = round(float(value), 2)
        self.OnPropertyChanged("Temp2")

    @property
    def Temp3(self) -> float:
        return self._Temp3

    @Temp3.setter
    def Temp3(self, value: float) -> None:
        self._Temp3 = round(float(value), 2)
        self.OnPropertyChanged("Temp3")

    @property
    def Temp4(self) -> float:
        return self._Temp4

    @Temp4.setter
    def Temp4(self, value: float) -> None:
        self._Temp4 = round(float(value), 2)
        self.OnPropertyChanged("Temp4")

    @property
    def Temp1On(self) -> bool:
        return self._Temp1On

    @Temp1On.setter
    def Temp1On(self, value: bool) -> None:
        if self._Temp1On != bool(value):
            self._Temp1On = bool(value)
            self.OnPropertyChanged("Temp1On")

    @property
    def Temp2On(self) -> bool:
        return self._Temp2On

    @Temp2On.setter
    def Temp2On(self, value: bool) -> None:
        if self._Temp2On != bool(value):
            self._Temp2On = bool(value)
            self.OnPropertyChanged("Temp2On")

    @property
    def Temp3On(self) -> bool:
        return self._Temp3On

    @Temp3On.setter
    def Temp3On(self, value: bool) -> None:
        if self._Temp3On != bool(value):
            self._Temp3On = bool(value)
            self.OnPropertyChanged("Temp3On")

    @property
    def Temp4On(self) -> bool:
        return self._Temp4On

    @Temp4On.setter
    def Temp4On(self, value: bool) -> None:
        if self._Temp4On != bool(value):
            self._Temp4On = bool(value)
            self.OnPropertyChanged("Temp4On")

    @property
    def CurrT(self) -> str:
        return self._CurrT

    @CurrT.setter
    def CurrT(self, value: str) -> None:
        self._CurrT = str(value)
        self.OnPropertyChanged("CurrT")

    @property
    def isTuning(self) -> bool:
        return self._isTuning

    @isTuning.setter
    def isTuning(self, value: bool) -> None:
        if self._isTuning != bool(value):
            self._isTuning = bool(value)
            self.OnPropertyChanged("isTuning")

    def OnPropertyChanged(self, property_name: str) -> None:
        for callback in list(self.PropertyChanged):
            callback(self, property_name)
