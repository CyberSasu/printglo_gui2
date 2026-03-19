from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock


class Logger:
    _lock = Lock()
    _log_path = Path(__file__).resolve().with_name("printgloo.log")

    @staticmethod
    def Log(message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with Logger._lock:
            with Logger._log_path.open("a", encoding="utf-8") as file:
                file.write(f"{timestamp} {message}\n")
