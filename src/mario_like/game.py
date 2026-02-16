from __future__ import annotations

import pygame

from . import settings


class Player:
    def __init__(self, x: int, y: int, width: int = 36, height: int = 48) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity_y = 0.0
        self.on_ground = False

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= settings.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += settings.PLAYER_SPEED

        self.rect.x += dx

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.velocity_y = settings.JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self) -> None:
        self.velocity_y += settings.GRAVITY
        self.rect.y += int(self.velocity_y)

    def resolve_collisions(self, platforms: list[pygame.Rect]) -> None:
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity_y >= 0:
                self.rect.bottom = platform.top
                self.velocity_y = 0
                self.on_ground = True


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player(120, 160)
        self.platforms = [
            pygame.Rect(0, settings.SCREEN_HEIGHT - 40, settings.SCREEN_WIDTH, 40),
            pygame.Rect(170, settings.SCREEN_HEIGHT - 140, 180, 20),
            pygame.Rect(460, settings.SCREEN_HEIGHT - 220, 220, 20),
        ]

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_gravity()
        self.player.resolve_collisions(self.platforms)

        if self.player.rect.top > settings.SCREEN_HEIGHT:
            self.player.rect.topleft = (120, 80)
            self.player.velocity_y = 0

    def render(self) -> None:
        self.screen.fill((92, 186, 255))

        for platform in self.platforms:
            pygame.draw.rect(self.screen, (52, 128, 52), platform)

        pygame.draw.rect(self.screen, (220, 64, 64), self.player.rect)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(settings.FPS)
