from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Level = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Diagnostic:
    level: Level
    code: str
    key_path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "code": self.code,
            "key_path": self.key_path,
            "message": self.message,
        }
