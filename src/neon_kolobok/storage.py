from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .settings import SAVE_FILE


@dataclass
class SaveData:
    best_times: dict[str, float] = field(default_factory=dict)
    best_deaths: dict[str, int] = field(default_factory=dict)
    leaderboard: list[dict[str, object]] = field(default_factory=list)
    settings: dict[str, object] = field(
        default_factory=lambda: {"music": 0.5, "sfx": 0.65, "fullscreen": False}
    )


class SaveManager:
    def __init__(self, path: Path = SAVE_FILE) -> None:
        self.path = path

    def load(self) -> SaveData:
        if not self.path.exists():
            return SaveData()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return SaveData()
        return SaveData(
            best_times={k: float(v) for k, v in data.get("best_times", {}).items()},
            best_deaths={k: int(v) for k, v in data.get("best_deaths", {}).items()},
            leaderboard=list(data.get("leaderboard", []))[:10],
            settings={**SaveData().settings, **data.get("settings", {})},
        )

    def write(self, save: SaveData) -> None:
        payload = {
            "best_times": save.best_times,
            "best_deaths": save.best_deaths,
            "leaderboard": save.leaderboard[:10],
            "settings": save.settings,
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def push_record(self, save: SaveData, mode: str, time_s: float, deaths: int) -> None:
        save.leaderboard.append({"mode": mode, "time": round(time_s, 3), "deaths": deaths})
        save.leaderboard.sort(key=lambda item: (item["time"], item["deaths"]))
        save.leaderboard = save.leaderboard[:10]
        prev_time = save.best_times.get(mode)
        if prev_time is None or time_s < prev_time:
            save.best_times[mode] = round(time_s, 3)
        prev_deaths = save.best_deaths.get(mode)
        if prev_deaths is None or deaths < prev_deaths:
            save.best_deaths[mode] = deaths
