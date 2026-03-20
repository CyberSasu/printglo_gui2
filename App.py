from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from MainWindow import MainWindow
from TkMainWindow import TkMainWindow


class App:
    def __init__(
        self,
        settings_path: str | Path | None = None,
        message_handler: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.settings_path = Path(settings_path) if settings_path else Path(__file__).resolve().with_name("Settings.json")
        self.message_handler = message_handler

    def CreateMainWindow(self) -> MainWindow:
        return MainWindow(settings_path=self.settings_path, message_handler=self.message_handler)

    def CreateUI(self) -> TkMainWindow:
        return TkMainWindow(settings_path=self.settings_path)

    def Run(self) -> None:
        self.CreateUI().run()


if __name__ == "__main__":
    App().Run()
