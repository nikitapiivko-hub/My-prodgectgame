"""Entry point for running the pygame prototype."""

import pygame

from .game import Game
from .settings import SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    game = Game(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
