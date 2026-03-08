from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Platform:
    rect: pygame.Rect
    zone: int
    vanish_period: float = 0.0
    vanish_offset: float = 0.0

    def active(self, t: float) -> bool:
        if self.vanish_period <= 0:
            return True
        return ((t + self.vanish_offset) % self.vanish_period) < self.vanish_period * 0.58


@dataclass
class Hazard:
    rect: pygame.Rect
    kind: str
    zone: int
    period: float = 0.0

    def active(self, t: float) -> bool:
        if self.kind != "laser":
            return True
        return (t % self.period) < self.period * 0.54


@dataclass
class BoostZone:
    rect: pygame.Rect
    factor: float
    zone: int


def build_tower(width: int = 1280) -> tuple[list[Platform], list[Hazard], list[BoostZone], dict[int, int]]:
    plats: list[Platform] = [Platform(pygame.Rect(0, 260, width, 40), 0)]
    hazards: list[Hazard] = []
    boosts: list[BoostZone] = []
    checkpoints = {0: 220, 1: -800, 2: -1700, 3: -2700}

    y = 140
    for i in range(32):
        y -= 120
        lane = i % 4
        px = 120 + lane * 250
        plats.append(Platform(pygame.Rect(px, y, 210, 24), 1 if y > -1300 else 2))
        if i > 4 and i % 3 == 0:
            hazards.append(Hazard(pygame.Rect(px + 50, y - 20, 110, 18), "spike", 1 if y > -1300 else 2))

    for j in range(18):
        y -= 135
        px = 60 + (j % 3) * 360
        vanish = 2.6 if j > 3 else 0.0
        plats.append(Platform(pygame.Rect(px, y, 200, 24), 2 if y > -2600 else 3, vanish, j * 0.25))
        if j % 2 == 0:
            hazards.append(Hazard(pygame.Rect(0, y - 80, width, 8), "laser", 2 if y > -2600 else 3, 2.4))
        if j % 4 == 1:
            boosts.append(BoostZone(pygame.Rect(px + 20, y - 45, 160, 25), 1.55, 3))

    for k in range(14):
        y -= 140
        px = 100 + (k % 5) * 220
        plats.append(Platform(pygame.Rect(px, y, 145, 22), 4, 2.0, k * 0.3))
        if k % 2 == 1:
            hazards.append(Hazard(pygame.Rect(px - 20, y - 34, 185, 16), "spike", 4))

    plats.append(Platform(pygame.Rect(width // 2 - 150, -4080, 300, 25), 4))
    return plats, hazards, boosts, checkpoints
