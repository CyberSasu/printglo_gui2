from __future__ import annotations

from typing import Any, Callable


class CommandModel:
    def __init__(self) -> None:
        self.PropertyChanged: list[Callable[[Any, str], None]] = []

        self._StopMotion: str | None = None
        self._Temp1On: str | None = None
        self._Temp2On: str | None = None
        self._Temp3On: str | None = None
        self._Temp4On: str | None = None
        self._Temp1Off: str | None = None
        self._Temp2Off: str | None = None
        self._Temp3Off: str | None = None
        self._Temp4Off: str | None = None
        self._Fan1: str | None = None
        self._Fan2: str | None = None
        self._Fan3: str | None = None
        self._TempRead: str | None = None
        self._Temp1Text: str | None = None
        self._Temp2Text: str | None = None
        self._Temp3Text: str | None = None
        self._Temp4Text: str | None = None
        self._Auger: str | None = None
        self._Puller: str | None = None
        self._Spooler: str | None = None
        self._Winder: str | None = None
        self._WinderSetPos: str | None = None
        self._WinderMove: str | None = None
        self._OpMotion: str | None = None
        self._FRead: str | None = None
        self._OpPreset: str | None = None

    @property
    def StopMotion(self) -> str | None:
        return self._StopMotion

    @StopMotion.setter
    def StopMotion(self, value: str | None) -> None:
        self._StopMotion = value
        self.OnPropertyChanged("StopMotion")

    @property
    def Temp1On(self) -> str | None:
        return self._Temp1On

    @Temp1On.setter
    def Temp1On(self, value: str | None) -> None:
        self._Temp1On = value
        self.OnPropertyChanged("Temp1On")

    @property
    def Temp2On(self) -> str | None:
        return self._Temp2On

    @Temp2On.setter
    def Temp2On(self, value: str | None) -> None:
        self._Temp2On = value
        self.OnPropertyChanged("Temp2On")

    @property
    def Temp3On(self) -> str | None:
        return self._Temp3On

    @Temp3On.setter
    def Temp3On(self, value: str | None) -> None:
        self._Temp3On = value
        self.OnPropertyChanged("Temp3On")

    @property
    def Temp4On(self) -> str | None:
        return self._Temp4On

    @Temp4On.setter
    def Temp4On(self, value: str | None) -> None:
        self._Temp4On = value
        self.OnPropertyChanged("Temp4On")

    @property
    def Temp1Off(self) -> str | None:
        return self._Temp1Off

    @Temp1Off.setter
    def Temp1Off(self, value: str | None) -> None:
        self._Temp1Off = value
        self.OnPropertyChanged("Temp1Off")

    @property
    def Temp2Off(self) -> str | None:
        return self._Temp2Off

    @Temp2Off.setter
    def Temp2Off(self, value: str | None) -> None:
        self._Temp2Off = value
        self.OnPropertyChanged("Temp2Off")

    @property
    def Temp3Off(self) -> str | None:
        return self._Temp3Off

    @Temp3Off.setter
    def Temp3Off(self, value: str | None) -> None:
        self._Temp3Off = value
        self.OnPropertyChanged("Temp3Off")

    @property
    def Temp4Off(self) -> str | None:
        return self._Temp4Off

    @Temp4Off.setter
    def Temp4Off(self, value: str | None) -> None:
        self._Temp4Off = value
        self.OnPropertyChanged("Temp4Off")

    @property
    def Fan1(self) -> str | None:
        return self._Fan1

    @Fan1.setter
    def Fan1(self, value: str | None) -> None:
        self._Fan1 = value
        self.OnPropertyChanged("Fan1")

    @property
    def Fan2(self) -> str | None:
        return self._Fan2

    @Fan2.setter
    def Fan2(self, value: str | None) -> None:
        self._Fan2 = value
        self.OnPropertyChanged("Fan2")

    @property
    def Fan3(self) -> str | None:
        return self._Fan3

    @Fan3.setter
    def Fan3(self, value: str | None) -> None:
        self._Fan3 = value
        self.OnPropertyChanged("Fan3")

    @property
    def TempRead(self) -> str | None:
        return self._TempRead

    @TempRead.setter
    def TempRead(self, value: str | None) -> None:
        self._TempRead = value
        self.OnPropertyChanged("TempRead")

    @property
    def Temp1Text(self) -> str | None:
        return self._Temp1Text

    @Temp1Text.setter
    def Temp1Text(self, value: str | None) -> None:
        self._Temp1Text = value
        self.OnPropertyChanged("Temp1Text")

    @property
    def Temp2Text(self) -> str | None:
        return self._Temp2Text

    @Temp2Text.setter
    def Temp2Text(self, value: str | None) -> None:
        self._Temp2Text = value
        self.OnPropertyChanged("Temp2Text")

    @property
    def Temp3Text(self) -> str | None:
        return self._Temp3Text

    @Temp3Text.setter
    def Temp3Text(self, value: str | None) -> None:
        self._Temp3Text = value
        self.OnPropertyChanged("Temp3Text")

    @property
    def Temp4Text(self) -> str | None:
        return self._Temp4Text

    @Temp4Text.setter
    def Temp4Text(self, value: str | None) -> None:
        self._Temp4Text = value
        self.OnPropertyChanged("Temp4Text")

    @property
    def Auger(self) -> str | None:
        return self._Auger

    @Auger.setter
    def Auger(self, value: str | None) -> None:
        self._Auger = value
        self.OnPropertyChanged("Auger")

    @property
    def Puller(self) -> str | None:
        return self._Puller

    @Puller.setter
    def Puller(self, value: str | None) -> None:
        self._Puller = value
        self.OnPropertyChanged("Puller")

    @property
    def Spooler(self) -> str | None:
        return self._Spooler

    @Spooler.setter
    def Spooler(self, value: str | None) -> None:
        self._Spooler = value
        self.OnPropertyChanged("Spooler")

    @property
    def Winder(self) -> str | None:
        return self._Winder

    @Winder.setter
    def Winder(self, value: str | None) -> None:
        self._Winder = value
        self.OnPropertyChanged("Winder")

    @property
    def WinderSetPos(self) -> str | None:
        return self._WinderSetPos

    @WinderSetPos.setter
    def WinderSetPos(self, value: str | None) -> None:
        self._WinderSetPos = value
        self.OnPropertyChanged("WinderSetPos")

    @property
    def WinderMove(self) -> str | None:
        return self._WinderMove

    @WinderMove.setter
    def WinderMove(self, value: str | None) -> None:
        self._WinderMove = value
        self.OnPropertyChanged("WinderMove")

    @property
    def OpMotion(self) -> str | None:
        return self._OpMotion

    @OpMotion.setter
    def OpMotion(self, value: str | None) -> None:
        self._OpMotion = value
        self.OnPropertyChanged("OpMotion")

    @property
    def FRead(self) -> str | None:
        return self._FRead

    @FRead.setter
    def FRead(self, value: str | None) -> None:
        self._FRead = value
        self.OnPropertyChanged("FRead")

    @property
    def OpPreset(self) -> str | None:
        return self._OpPreset

    @OpPreset.setter
    def OpPreset(self, value: str | None) -> None:
        self._OpPreset = value
        self.OnPropertyChanged("OpPreset")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "StopMotion": self.StopMotion,
            "Temp1On": self.Temp1On,
            "Temp2On": self.Temp2On,
            "Temp3On": self.Temp3On,
            "Temp4On": self.Temp4On,
            "Temp1Off": self.Temp1Off,
            "Temp2Off": self.Temp2Off,
            "Temp3Off": self.Temp3Off,
            "Temp4Off": self.Temp4Off,
            "Fan1": self.Fan1,
            "Fan2": self.Fan2,
            "Fan3": self.Fan3,
            "TempRead": self.TempRead,
            "Temp1Text": self.Temp1Text,
            "Temp2Text": self.Temp2Text,
            "Temp3Text": self.Temp3Text,
            "Temp4Text": self.Temp4Text,
            "Auger": self.Auger,
            "Puller": self.Puller,
            "Spooler": self.Spooler,
            "Winder": self.Winder,
            "WinderSetPos": self.WinderSetPos,
            "WinderMove": self.WinderMove,
            "OpMotion": self.OpMotion,
            "FRead": self.FRead,
            "OpPreset": self.OpPreset,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "CommandModel":
        model = cls()
        if not data:
            return model

        for key in model.to_dict().keys():
            if key in data:
                setattr(model, key, data[key])
        return model

    def OnPropertyChanged(self, property_name: str) -> None:
        for callback in list(self.PropertyChanged):
            callback(self, property_name)
