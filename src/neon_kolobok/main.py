from __future__ import annotations

import os

import pygame

from .game import NeonKolobokGame
from .settings import SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


def main() -> None:
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = NeonKolobokGame(screen)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
