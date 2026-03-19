from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from Models.CommandModel import CommandModel
from Models.ValueModel import ValueModel


class SettingModel:
    def __init__(
        self,
        settings_path: str | Path | None = None,
        message_handler: Callable[[str], None] | None = None,
    ) -> None:
        self.PropertyChanged: list[Callable[[Any, str], None]] = []
        self.settings_path = Path(settings_path) if settings_path else Path(__file__).resolve().parents[1] / "Settings.json"
        self.message_handler = message_handler or self._default_message_handler

        self.FirmwareVersion: str | None = None
        self._commands: CommandModel = CommandModel()
        self._values: ValueModel = ValueModel()

    @property
    def commands(self) -> CommandModel:
        return self._commands

    @commands.setter
    def commands(self, value: CommandModel) -> None:
        if self._commands != value:
            self._commands = value
            self.OnPropertyChanged("commands")

    @property
    def values(self) -> ValueModel:
        return self._values

    @values.setter
    def values(self, value: ValueModel) -> None:
        if self._values != value:
            self._values = value
            self.OnPropertyChanged("values")

    def ReadSettings(self) -> "SettingModel":
        try:
            with self.settings_path.open("r", encoding="utf-8") as file:
                json_content = json.load(file)
            return SettingModel.from_dict(
                json_content,
                settings_path=self.settings_path,
                message_handler=self.message_handler,
            )
        except Exception:
            default_model = SettingModel(settings_path=self.settings_path, message_handler=self.message_handler)
            self.WriteSettings(default_model)
            self.message_handler("Error with Settings! contact Freelancer")
            return default_model

    def WriteSettings(self, s: "SettingModel") -> None:
        json_content = json.dumps(s.to_dict(), indent=2)
        with self.settings_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(json_content)
            file.write("\n")

    def to_dict(self) -> dict[str, Any]:
        return {
            "FirmwareVersion": self.FirmwareVersion,
            "commands": self.commands.to_dict(),
            "values": self.values.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any] | None,
        settings_path: str | Path | None = None,
        message_handler: Callable[[str], None] | None = None,
    ) -> "SettingModel":
        model = cls(settings_path=settings_path, message_handler=message_handler)
        if not data:
            return model

        model.FirmwareVersion = data.get("FirmwareVersion")
        model.commands = CommandModel.from_dict(data.get("commands"))
        model.values = ValueModel.from_dict(data.get("values"))
        return model

    def OnPropertyChanged(self, property_name: str) -> None:
        for callback in list(self.PropertyChanged):
            callback(self, property_name)

    @staticmethod
    def _default_message_handler(message: str) -> None:
        print(message)
