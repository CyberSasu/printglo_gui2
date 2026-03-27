from __future__ import annotations

import math
from typing import Any, Callable


def _clamp(value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if math.isnan(value):
        return value
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def _coerce_non_negative(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    if math.isnan(number) or math.isinf(number):
        return float(default)
    return max(0.0, number)


def _coerce_positive_int(value: Any, default: int = 1) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return int(default)
    return max(1, number)


class ValueModel:
    def __init__(self) -> None:
        self.PropertyChanged: list[Callable[[Any, str], None]] = []

        self.MinTemp: float = 0
        self.MaxTemp: float = 0

        self._TuningTemp: int = 0
        self._TuningCycles: int = 0
        self._TuningP: float = 0
        self._TuningI: float = 0
        self._TuningD: float = 0

        self._Fan1: int = 0
        self._Fan2: int = 0
        self._Fan3: int = 0

        self._Auger: float = 0
        self._Winder: float = 0
        self._Spooler: float = 0
        self.CalcWinder: float = 0
        self._WinderMax: float = 0
        self._WinderLimit: float = 0
        self._SpoolerID: float = 0
        self._SpoolerOD: float = 0
        self._Puller: float = 0
        self._WinderStart: float = 0
        self._SpoolingDirection: str = "Right"

        self.PullerDia: float = 0
        self.Spmm: float = 0
        self.SpoolerSpmm: float = 0
        self.WinderSpmm: float = 0
        self.WinderPitch: float = 0

        self.PullerP: float = 0
        self.PullerI: float = 0
        self.PullerD: float = 0
        self.PIDInterval: int = 0
        self.LastPullerD: float = 0
        self.MinPID: float = 0
        self.MaxPID: float = 0
        self.IntegratorWindPID: float = 0
        self.K1: float = 0
        self.K2: float = 0
        self.dia_iState_fwidth: float = 0
        self.puller_increment: float = 0

        self._FDia: float = 0
        self.CurrFDia: list[float] = []
        self.LastFDia: float = 0
        self._ReadFDia: float = 0

        self.OpDelay: int = 0

    @property
    def TuningTemp(self) -> int:
        return self._TuningTemp

    @TuningTemp.setter
    def TuningTemp(self, value: int) -> None:
        value = int(value)
        if self._TuningTemp != value:
            self._TuningTemp = int(_clamp(value, 50, 450))
            self.OnPropertyChanged("TuningTemp")

    @property
    def TuningCycles(self) -> int:
        return self._TuningCycles

    @TuningCycles.setter
    def TuningCycles(self, value: int) -> None:
        value = int(value)
        if self._TuningCycles != value:
            self._TuningCycles = int(_clamp(value, 1, 30))
            self.OnPropertyChanged("TuningCycles")

    @property
    def TuningP(self) -> float:
        return self._TuningP

    @TuningP.setter
    def TuningP(self, value: float) -> None:
        value = float(value)
        if self._TuningP != value:
            self._TuningP = value
            self.OnPropertyChanged("TuningP")

    @property
    def TuningI(self) -> float:
        return self._TuningI

    @TuningI.setter
    def TuningI(self, value: float) -> None:
        value = float(value)
        if self._TuningI != value:
            self._TuningI = value
            self.OnPropertyChanged("TuningI")

    @property
    def TuningD(self) -> float:
        return self._TuningD

    @TuningD.setter
    def TuningD(self, value: float) -> None:
        value = float(value)
        if self._TuningD != value:
            self._TuningD = value
            self.OnPropertyChanged("TuningD")

    @property
    def Fan1(self) -> int:
        return self._Fan1

    @Fan1.setter
    def Fan1(self, value: int) -> None:
        self._Fan1 = int(_clamp(int(value), 0, 100))
        self.OnPropertyChanged("Fan1")

    @property
    def Fan2(self) -> int:
        return self._Fan2

    @Fan2.setter
    def Fan2(self, value: int) -> None:
        self._Fan2 = int(_clamp(int(value), 0, 100))
        self.OnPropertyChanged("Fan2")

    @property
    def Fan3(self) -> int:
        return self._Fan3

    @Fan3.setter
    def Fan3(self, value: int) -> None:
        self._Fan3 = int(_clamp(int(value), 0, 100))
        self.OnPropertyChanged("Fan3")

    @property
    def Auger(self) -> float:
        return self._Auger

    @Auger.setter
    def Auger(self, value: float) -> None:
        value = float(value)
        if self._Auger != value:
            self._Auger = _clamp(value, 0, 150)
            self.OnPropertyChanged("Auger")

    @property
    def Winder(self) -> float:
        return self._Winder

    @Winder.setter
    def Winder(self, value: float) -> None:
        value = float(value)
        if self._Winder != value:
            self._Winder = _clamp(value, 0, 300)
            self.OnPropertyChanged("Winder")

    @property
    def Spooler(self) -> float:
        return self._Spooler

    @Spooler.setter
    def Spooler(self, value: float) -> None:
        value = float(value)
        if self._Spooler != value:
            self._Spooler = _clamp(value, 0, 20)
            self.OnPropertyChanged("Spooler")

    @property
    def WinderMax(self) -> float:
        return self._WinderMax

    @WinderMax.setter
    def WinderMax(self, value: float) -> None:
        value = float(value)
        if self._WinderMax != value:
            self._WinderMax = _clamp(value, 0, 120)
            self.OnPropertyChanged("WinderMax")

    @property
    def WinderLimit(self) -> float:
        return self._WinderLimit

    @WinderLimit.setter
    def WinderLimit(self, value: float) -> None:
        value = float(value)
        if self._WinderLimit != value:
            self._WinderLimit = _clamp(value, 0, float("inf"))
            self.OnPropertyChanged("WinderLimit")

    @property
    def SpoolerID(self) -> float:
        return self._SpoolerID

    @SpoolerID.setter
    def SpoolerID(self, value: float) -> None:
        value = float(value)
        if self._SpoolerID != value:
            self._SpoolerID = _clamp(value, 0, float("inf"))
            self.OnPropertyChanged("SpoolerID")

    @property
    def SpoolerOD(self) -> float:
        return self._SpoolerOD

    @SpoolerOD.setter
    def SpoolerOD(self, value: float) -> None:
        value = float(value)
        if self._SpoolerOD != value:
            self._SpoolerOD = _clamp(value, 0, float("inf"))
            self.OnPropertyChanged("SpoolerOD")

    @property
    def Puller(self) -> float:
        return self._Puller

    @Puller.setter
    def Puller(self, value: float) -> None:
        value = float(value)
        if self._Puller != value:
            self._Puller = _clamp(value, 0, 300)
            self.OnPropertyChanged("Puller")

    @property
    def WinderStart(self) -> float:
        return self._WinderStart

    @WinderStart.setter
    def WinderStart(self, value: float) -> None:
        value = float(value)
        if self._WinderStart != value:
            self._WinderStart = _clamp(value, 0, float("inf"))
            self.OnPropertyChanged("WinderStart")

    @property
    def SpoolingDirection(self) -> str:
        return self._SpoolingDirection

    @SpoolingDirection.setter
    def SpoolingDirection(self, value: str) -> None:
        direction = str(value).strip().lower()
        normalized = "Left" if direction == "left" else "Right"
        if self._SpoolingDirection != normalized:
            self._SpoolingDirection = normalized
            self.OnPropertyChanged("SpoolingDirection")

    @property
    def FDia(self) -> float:
        return self._FDia

    @FDia.setter
    def FDia(self, value: float) -> None:
        value = float(value)
        if self._FDia != value:
            self._FDia = value
            self.OnPropertyChanged("FDia")

    @property
    def ReadFDia(self) -> float:
        return self._ReadFDia

    @ReadFDia.setter
    def ReadFDia(self, value: float) -> None:
        self._ReadFDia = float(value)
        self.OnPropertyChanged("ReadFDia")

    def to_dict(self) -> dict[str, Any]:
        return {
            "MinTemp": self.MinTemp,
            "MaxTemp": self.MaxTemp,
            "TuningTemp": self.TuningTemp,
            "TuningCycles": self.TuningCycles,
            "TuningP": self.TuningP,
            "TuningI": self.TuningI,
            "TuningD": self.TuningD,
            "Fan1": self.Fan1,
            "Fan2": self.Fan2,
            "Fan3": self.Fan3,
            "Auger": self.Auger,
            "Winder": self.Winder,
            "Spooler": self.Spooler,
            "WinderMax": self.WinderMax,
            "WinderLimit": self.WinderLimit,
            "SpoolerID": self.SpoolerID,
            "SpoolerOD": self.SpoolerOD,
            "Puller": self.Puller,
            "WinderStart": self.WinderStart,
            "SpoolingDirection": self.SpoolingDirection,
            "PullerDia": self.PullerDia,
            "Spmm": self.Spmm,
            "SpoolerSpmm": self.SpoolerSpmm,
            "WinderSpmm": self.WinderSpmm,
            "WinderPitch": self.WinderPitch,
            "PullerP": self.PullerP,
            "PullerI": self.PullerI,
            "PullerD": self.PullerD,
            "PIDInterval": self.PIDInterval,
            "MinPID": self.MinPID,
            "MaxPID": self.MaxPID,
            "IntegratorWindPID": self.IntegratorWindPID,
            "K1": self.K1,
            "K2": self.K2,
            "dia_iState_fwidth": self.dia_iState_fwidth,
            "puller_increment": self.puller_increment,
            "FDia": self.FDia,
            "OpDelay": self.OpDelay,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ValueModel":
        model = cls()
        if not data:
            return model

        if "MinTemp" in data:
            model.MinTemp = _coerce_non_negative(data["MinTemp"])
        if "MaxTemp" in data:
            model.MaxTemp = _coerce_non_negative(data["MaxTemp"])
        if model.MaxTemp and model.MinTemp > model.MaxTemp:
            model.MinTemp, model.MaxTemp = model.MaxTemp, model.MinTemp

        model.PullerDia = _coerce_non_negative(data.get("PullerDia", model.PullerDia))
        model.Spmm = _coerce_non_negative(data.get("Spmm", model.Spmm))
        model.SpoolerSpmm = _coerce_non_negative(data.get("SpoolerSpmm", model.SpoolerSpmm))
        model.WinderSpmm = _coerce_non_negative(data.get("WinderSpmm", model.WinderSpmm))
        model.WinderPitch = _coerce_non_negative(data.get("WinderPitch", model.WinderPitch))
        model.PullerP = _coerce_non_negative(data.get("PullerP", model.PullerP))
        model.PullerI = _coerce_non_negative(data.get("PullerI", model.PullerI))
        model.PullerD = _coerce_non_negative(data.get("PullerD", model.PullerD))
        model.PIDInterval = _coerce_positive_int(data.get("PIDInterval", model.PIDInterval or 1))
        model.MinPID = _coerce_non_negative(data.get("MinPID", model.MinPID))
        model.MaxPID = _coerce_non_negative(data.get("MaxPID", model.MaxPID))
        if model.MaxPID and model.MinPID > model.MaxPID:
            model.MinPID, model.MaxPID = model.MaxPID, model.MinPID
        model.IntegratorWindPID = _coerce_non_negative(data.get("IntegratorWindPID", model.IntegratorWindPID))
        model.K1 = _coerce_non_negative(data.get("K1", model.K1))
        model.K2 = _coerce_non_negative(data.get("K2", model.K2))
        model.dia_iState_fwidth = float(data.get("dia_iState_fwidth", model.dia_iState_fwidth) or 0.0)
        model.puller_increment = _coerce_positive_int(data.get("puller_increment", model.puller_increment or 1))
        model.OpDelay = _coerce_positive_int(data.get("OpDelay", model.OpDelay or 1), default=1)

        property_fields = [
            "TuningTemp",
            "TuningCycles",
            "TuningP",
            "TuningI",
            "TuningD",
            "Fan1",
            "Fan2",
            "Fan3",
            "Auger",
            "Winder",
            "Spooler",
            "WinderMax",
            "WinderLimit",
            "SpoolerID",
            "SpoolerOD",
            "Puller",
            "WinderStart",
            "SpoolingDirection",
            "FDia",
        ]

        for field_name in property_fields:
            if field_name in data:
                setattr(model, field_name, data[field_name])

        return model

    def OnPropertyChanged(self, property_name: str) -> None:
        for callback in list(self.PropertyChanged):
            callback(self, property_name)
