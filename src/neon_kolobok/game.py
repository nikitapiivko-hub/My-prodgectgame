from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from .audio import AudioBank
from .level import BoostZone, Hazard, Platform, build_tower
from .settings import (
    AIR_CONTROL,
    COLORS,
    FINISH_Y,
    FPS,
    GRAVITY,
    JUMP_SPEED,
    MAX_FALL_SPEED,
    MOVE_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    START_Y,
    TARGET_DT,
    TITLE,
)
from .storage import SaveData, SaveManager


@dataclass
class Player:
    x: float = 170
    y: float = START_Y
    vx: float = 0
    vy: float = 0
    radius: int = 20
    on_ground: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)


class NeonKolobokGame:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("consolas", 24)
        self.big = pygame.font.SysFont("consolas", 42, bold=True)

        self.save_manager = SaveManager()
        self.save = self.save_manager.load()
        self.audio = AudioBank(float(self.save.settings["sfx"]), float(self.save.settings["music"]))
        self.audio.play_ambient()

        self.platforms, self.hazards, self.boosts, self.checkpoints = build_tower(SCREEN_WIDTH)
        self.mode = "normal"
        self.state = "menu"
        self.player = Player()
        self.camera_y = 0.0
        self.trail: list[tuple[float, float, float]] = []
        self.total_deaths = 0
        self.run_time = 0.0
        self.flash = 0.0
        self.shake = 0.0
        self.current_checkpoint = START_Y

    def reset_run(self) -> None:
        self.player = Player(y=self.current_checkpoint if self.mode == "practice" else START_Y)
        self.camera_y = 0
        self.trail.clear()
        self.run_time = 0.0
        self.total_deaths = 0
        self.flash = 0.0

    def start_mode(self, mode: str) -> None:
        self.mode = mode
        self.state = "playing"
        self.current_checkpoint = START_Y
        self.reset_run()

    def apply_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move += 1

        accel = MOVE_SPEED * (1.0 if self.player.on_ground else AIR_CONTROL)
        self.player.vx = move * accel

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.player.on_ground:
            self.player.vy = -JUMP_SPEED
            self.player.on_ground = False
            if self.audio.ready:
                self.audio.jump.play()

        self.player.vy = min(MAX_FALL_SPEED, self.player.vy + GRAVITY * dt)
        self.player.x += self.player.vx * dt
        self.player.y += self.player.vy * dt

    def _screen_y(self, world_y: float) -> float:
        return world_y - self.camera_y

    def collisions(self) -> None:
        p_rect = self.player.rect()
        self.player.on_ground = False
        t = self.run_time

        for platform in self.platforms:
            if not platform.active(t):
                continue
            rect = platform.rect
            if p_rect.colliderect(rect) and self.player.vy >= 0 and p_rect.bottom - self.player.vy * TARGET_DT <= rect.top + 8:
                self.player.y = rect.top - self.player.radius
                self.player.vy = 0
                self.player.on_ground = True
                p_rect = self.player.rect()

        for boost in self.boosts:
            if p_rect.colliderect(boost.rect):
                self.player.vx *= boost.factor

        for hazard in self.hazards:
            if hazard.active(t) and p_rect.colliderect(hazard.rect):
                self.kill_player()
                return

        if self.player.y > 360:
            self.kill_player()

    def kill_player(self) -> None:
        self.flash = 0.25
        self.shake = 0.35
        self.total_deaths += 1
        if self.audio.ready:
            self.audio.death.play()
        spawn = START_Y
        if self.mode == "practice":
            spawn = self.current_checkpoint
        elif self.mode == "normal" and self.player.y < -2200:
            spawn = -2100
        self.player = Player(y=spawn)

    def update_checkpoints(self) -> None:
        if self.mode != "practice":
            return
        for _, y in self.checkpoints.items():
            if self.player.y < y:
                self.current_checkpoint = y

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return
        self.run_time += dt
        self.apply_input(dt)
        self.collisions()
        self.update_checkpoints()
        self.camera_y = min(180, self.player.y + 120)
        self.trail.append((self.player.x, self.player.y, 1.0))
        self.trail = [(x, y, life - dt * 2.4) for x, y, life in self.trail if life - dt * 2.4 > 0]

        self.flash = max(0.0, self.flash - dt)
        self.shake = max(0.0, self.shake - dt)

        if self.player.y <= FINISH_Y:
            self.state = "win"
            self.save_manager.push_record(self.save, self.mode, self.run_time, self.total_deaths)
            self.save_manager.write(self.save)

    def draw_background(self) -> None:
        self.screen.fill(COLORS.bg_top)
        for i in range(0, SCREEN_HEIGHT, 6):
            mix = i / SCREEN_HEIGHT
            c = (
                int(COLORS.bg_top[0] * (1 - mix) + COLORS.bg_bottom[0] * mix),
                int(COLORS.bg_top[1] * (1 - mix) + COLORS.bg_bottom[1] * mix),
                int(COLORS.bg_top[2] * (1 - mix) + COLORS.bg_bottom[2] * mix),
            )
            pygame.draw.line(self.screen, c, (0, i), (SCREEN_WIDTH, i))
        for idx in range(9):
            x = (idx * 160 + int(self.camera_y * 0.2)) % (SCREEN_WIDTH + 240) - 120
            pygame.draw.polygon(self.screen, (55, 15, 24), [(x, SCREEN_HEIGHT), (x + 70, SCREEN_HEIGHT - 220), (x + 140, SCREEN_HEIGHT)])

    def draw_world(self) -> None:
        t = self.run_time
        for platform in self.platforms:
            y = int(self._screen_y(platform.rect.y))
            rect = pygame.Rect(platform.rect.x, y, platform.rect.width, platform.rect.height)
            if -50 <= rect.bottom <= SCREEN_HEIGHT + 50 and platform.active(t):
                zone_color = [COLORS.neon_cyan, COLORS.neon_magenta, COLORS.neon_orange, COLORS.neon_green, COLORS.neon_red][platform.zone % 5]
                pygame.draw.rect(self.screen, zone_color, rect, border_radius=4)

        for boost in self.boosts:
            y = int(self._screen_y(boost.rect.y))
            rect = pygame.Rect(boost.rect.x, y, boost.rect.width, boost.rect.height)
            if -30 <= rect.bottom <= SCREEN_HEIGHT + 30:
                pygame.draw.rect(self.screen, COLORS.neon_green, rect, 2, border_radius=6)

        for hazard in self.hazards:
            if not hazard.active(t):
                continue
            y = int(self._screen_y(hazard.rect.y))
            rect = pygame.Rect(hazard.rect.x, y, hazard.rect.width, hazard.rect.height)
            if -40 <= rect.bottom <= SCREEN_HEIGHT + 40:
                color = COLORS.neon_red if hazard.kind == "spike" else COLORS.neon_magenta
                pygame.draw.rect(self.screen, color, rect)

        for x, y, life in self.trail:
            sy = self._screen_y(y)
            pygame.draw.circle(self.screen, (80, 240, 255), (int(x), int(sy)), int(10 * life), 1)

        px, py = int(self.player.x), int(self._screen_y(self.player.y))
        glow = 30 + int(6 * math.sin(self.run_time * 7))
        pygame.draw.circle(self.screen, (255, 160, 75), (px, py), glow)
        pygame.draw.circle(self.screen, (255, 235, 140), (px, py), self.player.radius)
        pygame.draw.circle(self.screen, (10, 10, 18), (px - 6, py - 4), 3)
        pygame.draw.circle(self.screen, (10, 10, 18), (px + 6, py - 4), 3)
        pygame.draw.arc(self.screen, (40, 12, 25), pygame.Rect(px - 8, py - 1, 16, 12), 0.2, 2.9, 2)

    def draw_ui(self) -> None:
        y = 12
        for txt in (
            f"MODE: {self.mode.upper()}",
            f"TIME: {self.run_time:06.2f}",
            f"DEATHS: {self.total_deaths}",
            "R: restart  ESC: menu/pause  F11: fullscreen",
        ):
            self.screen.blit(self.font.render(txt, True, COLORS.text), (14, y))
            y += 28

    def draw_menu(self) -> None:
        lines = [
            TITLE,
            "1 - NORMAL (rare checkpoint)",
            "2 - HARDCORE (no checkpoint)",
            "3 - PRACTICE (frequent checkpoints)",
            "M - music on/off, N - sfx on/off",
            "A/D or arrows move, Space jump",
            "Local leaderboard:",
        ]
        for idx, line in enumerate(lines):
            font = self.big if idx == 0 else self.font
            self.screen.blit(font.render(line, True, COLORS.text), (80, 80 + idx * 52))
        for i, entry in enumerate(self.save.leaderboard[:5]):
            msg = f"{i+1}. {entry['mode']}  {entry['time']}s  deaths:{entry['deaths']}"
            self.screen.blit(self.font.render(msg, True, COLORS.neon_cyan), (120, 460 + i * 30))

    def draw_overlay(self, title: str) -> None:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 160))
        self.screen.blit(surface, (0, 0))
        self.screen.blit(self.big.render(title, True, COLORS.text), (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 20))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullscreen = bool(self.save.settings["fullscreen"])
            self.save.settings["fullscreen"] = not fullscreen
            flag = pygame.FULLSCREEN if not fullscreen else 0
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flag)

        if self.state == "menu" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.start_mode("normal")
            if event.key == pygame.K_2:
                self.start_mode("hardcore")
            if event.key == pygame.K_3:
                self.start_mode("practice")
            if event.key == pygame.K_m:
                self.save.settings["music"] = 0.0 if float(self.save.settings["music"]) > 0 else 0.55
            if event.key == pygame.K_n:
                self.save.settings["sfx"] = 0.0 if float(self.save.settings["sfx"]) > 0 else 0.65
            self.save_manager.write(self.save)

        if self.state == "playing" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.kill_player()
            if event.key == pygame.K_ESCAPE:
                self.state = "pause"

        elif self.state in {"pause", "win"} and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"

    def render(self) -> None:
        shake_x = int(math.sin(self.run_time * 90) * 6 * self.shake)
        shake_y = int(math.cos(self.run_time * 100) * 6 * self.shake)
        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        old = self.screen
        self.screen = canvas

        self.draw_background()
        if self.state in {"playing", "pause", "win"}:
            self.draw_world()
            self.draw_ui()
        else:
            self.draw_menu()

        if self.state == "pause":
            self.draw_overlay("PAUSED")
        if self.state == "win":
            self.draw_overlay("YOU ESCAPED HELL TOWER")
        if self.flash > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 90, 90, int(130 * self.flash / 0.25)))
            self.screen.blit(overlay, (0, 0))

        self.screen = old
        self.screen.blit(canvas, (shake_x, shake_y))
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = min(0.033, self.clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.render()
        self.audio.stop_ambient()
        self.save_manager.write(self.save)
