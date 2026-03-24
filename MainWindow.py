from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Callable

from Models.SettingModel import SettingModel
from ViewModels.ComViewModel import ComViewModel


class MainWindow:
    def __init__(
        self,
        settings_path: str | Path | None = None,
        message_handler: Callable[[str], None] | None = None,
    ) -> None:
        self.settings_path = Path(settings_path) if settings_path else Path(__file__).resolve().with_name("Settings.json")
        self.message_handler = message_handler or self._default_message_handler

        self.sett: SettingModel | None = None
        self.comViewModel: ComViewModel | None = None

        self.customCommandsHistory: list[str] = []
        self.customCommandPos = 0

        self.serialDataSent: list[str] = []
        self.serialDataReceived: list[str] = []

        self.DataContext = None
        self.Ext1TempSliderDataContext = None
        self.Ext2TempSliderDataContext = None
        self.Ext3TempSliderDataContext = None
        self.Ext4TempSliderDataContext = None

        self.PullerToggle = False
        self.AutoModeToggle = False

        self.InitializeModels()
        self.InitializeViewModels()
        self.SetDataContexts()
        self.SetActions()

    def InitializeModels(self) -> None:
        self.sett = SettingModel(settings_path=self.settings_path, message_handler=self.message_handler)
        self.sett = self.sett.ReadSettings()

    def InitializeViewModels(self) -> None:
        self.comViewModel = ComViewModel(self.sett, message_handler=self.message_handler)

    def SetDataContexts(self) -> None:
        self.DataContext = self.comViewModel
        self.Ext1TempSliderDataContext = self.comViewModel
        self.Ext2TempSliderDataContext = self.comViewModel
        self.Ext3TempSliderDataContext = self.comViewModel
        self.Ext4TempSliderDataContext = self.comViewModel

    def SetActions(self) -> None:
        self.comViewModel.add_OnCommandSent(self.UpdateUIOnCommandSent)
        self.comViewModel.add_OnResponseReceived(self.UpdateUIOnResponseReceived)

    def CheckCom(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.ComChecks()

    def ConnectCom(self, sender: object | None = None, e: object | None = None) -> bool:
        if self.comViewModel.ConnectCom():
            self.comViewModel.SetInitialConnectState()
            return True
        return False

    def DisconnectCom(self, sender: object | None = None, e: object | None = None) -> bool:
        return self.comViewModel.ComClose()

    def EmergencyClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.EmergencyStop()

    def ReadSettClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.sett = self.sett.ReadSettings()
        self.comViewModel.Setting = self.sett

    def TempClick(self, tag: str) -> None:
        if tag == "1":
            if self.comViewModel.comModel.Temp1On:
                self.comViewModel.TempOff("1")
            else:
                self.comViewModel.TempOn("1")
        elif tag == "2":
            if self.comViewModel.comModel.Temp2On:
                self.comViewModel.TempOff("2")
            else:
                self.comViewModel.TempOn("2")
        elif tag == "3":
            if self.comViewModel.comModel.Temp3On:
                self.comViewModel.TempOff("3")
            else:
                self.comViewModel.TempOn("3")
        elif tag == "4":
            if self.comViewModel.comModel.Temp4On:
                self.comViewModel.TempOff("4")
            else:
                self.comViewModel.TempOn("4")

    def MotorClick(self, tag: str) -> None:
        self.comViewModel.MotorControl(tag)

    def FanClick(self, is_checked: bool | None, tag: int) -> None:
        self.comViewModel.FanControl(is_checked is False, int(tag))

    def StartTuningClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.StartTuning()

    def SetPIDClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.SetPID()

    def StartOpClick(
        self,
        sender: object | None = None,
        e: object | None = None,
        PullerToggle: bool | None = None,
        AutoModeToggle: bool | None = None,
    ) -> None:
        if PullerToggle is not None:
            self.PullerToggle = PullerToggle
        if AutoModeToggle is not None:
            self.AutoModeToggle = AutoModeToggle

        self.comViewModel.isAutoMode = self.AutoModeToggle is True
        self.comViewModel.isPullerAuto = self.PullerToggle is True

        if self.PullerToggle is True:
            self.comViewModel.SetNewPuller()
            time.sleep(2.5)
        elif self.AutoModeToggle is True:
            self.comViewModel.AutoMode()

        self.comViewModel.StartOp()

    def StartSpoolingClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.StartSpooling()

    def StopOpClick(self, sender: object | None = None, e: object | None = None) -> None:
        self.comViewModel.StopOp()

    def CustomClick(self, command_text: str, sender: object | None = None, e: object | None = None) -> str:
        if len(command_text) < 2:
            return command_text
        self.CustomSent(command_text)
        return ""

    def CustomCommandEnter(self, key: str, current_text: str) -> str:
        if key == "Enter":
            if len(current_text) < 2:
                return current_text
            self.CustomSent(current_text)
            return ""
        if key == "Up":
            self.customCommandPos -= 1
            if self.customCommandPos < 0:
                self.customCommandPos = 0
            if self.customCommandPos < len(self.customCommandsHistory):
                return self.customCommandsHistory[self.customCommandPos]
            return current_text
        if key == "Down":
            self.customCommandPos += 1
            if self.customCommandPos >= len(self.customCommandsHistory):
                self.customCommandPos = len(self.customCommandsHistory)
                return ""
            if self.customCommandPos < len(self.customCommandsHistory):
                return self.customCommandsHistory[self.customCommandPos]
        return current_text

    def AppClose(
        self,
        sender: object | None = None,
        e: object | None = None,
        exit_process: bool = False,
    ) -> None:
        self.sett.WriteSettings(self.comViewModel.Setting)
        self.comViewModel.ComClose()
        time.sleep(0.25)
        if exit_process:
            raise SystemExit(0)

    def CustomSent(self, command: str) -> None:
        self.comViewModel.SendCommand(command)
        self.customCommandsHistory.append(command)
        if len(self.customCommandsHistory) > 150:
            self.customCommandsHistory.pop(0)
        self.customCommandPos = len(self.customCommandsHistory)

    def UpdateUIOnCommandSent(self, command: str) -> None:
        text = "Sent : " + command
        self.serialDataSent.append(text)

    def UpdateUIOnResponseReceived(self, response: str) -> None:
        text = "Received : " + response
        self.serialDataReceived.append(text)

    @staticmethod
    def _default_message_handler(message: str) -> None:
        print(message, file=sys.stderr)
