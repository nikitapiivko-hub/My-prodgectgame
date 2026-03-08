from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

TITLE = "Neon Kolobok: Hell Tower"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TARGET_DT = 1 / FPS

GRAVITY = 2300.0
MOVE_SPEED = 420.0
AIR_CONTROL = 0.8
JUMP_SPEED = 880.0
MAX_FALL_SPEED = 1150.0

TOWER_HEIGHT = 4200
START_Y = 160
FINISH_Y = -(TOWER_HEIGHT - 120)

SAVE_FILE = Path("save_data.json")


@dataclass(frozen=True)
class Colors:
    bg_top: tuple[int, int, int] = (8, 4, 18)
    bg_bottom: tuple[int, int, int] = (30, 4, 12)
    neon_orange: tuple[int, int, int] = (255, 130, 40)
    neon_magenta: tuple[int, int, int] = (255, 40, 170)
    neon_cyan: tuple[int, int, int] = (40, 255, 235)
    neon_red: tuple[int, int, int] = (255, 56, 56)
    neon_green: tuple[int, int, int] = (95, 255, 140)
    text: tuple[int, int, int] = (230, 245, 255)


COLORS = Colors()
