from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    root: Path
    raw: dict[str, Any]

    @property
    def project(self) -> dict[str, Any]:
        return self.raw["project"]

    @property
    def evolution(self) -> dict[str, Any]:
        return self.raw["evolution"]

    @property
    def evaluation(self) -> dict[str, Any]:
        return self.raw["evaluation"]

    @property
    def policy(self) -> dict[str, Any]:
        return self.raw["policy"]

    @property
    def quality_platform(self) -> dict[str, Any]:
        return self.raw.get("quality_platform", {"enabled": False, "required": False})

    @property
    def successor_model(self) -> dict[str, Any]:
        return self.raw.get("successor_model", {"enabled": False, "required": False})

    def path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else (self.root / path).resolve()


def load_settings(path: Path) -> Settings:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    required = ("project", "evolution", "evaluation", "policy")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"config missing sections: {', '.join(missing)}")
    return Settings(root=path.resolve().parents[1], raw=raw)
