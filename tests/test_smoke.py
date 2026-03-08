import os
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from neon_kolobok.game import NeonKolobokGame
from neon_kolobok.level import build_tower
from neon_kolobok.storage import SaveData, SaveManager


class SmokeTests(unittest.TestCase):
    def test_level_has_content(self):
        platforms, hazards, boosts, checkpoints = build_tower(1280)
        self.assertGreater(len(platforms), 30)
        self.assertGreater(len(hazards), 10)
        self.assertGreater(len(checkpoints), 2)
        self.assertGreater(len(boosts), 1)

    def test_game_can_tick_and_kill(self):
        pygame.init()
        screen = pygame.display.set_mode((640, 360))
        game = NeonKolobokGame(screen)
        game.start_mode("hardcore")
        game.player.y = 999
        deaths_before = game.total_deaths
        game.update(0.016)
        self.assertGreater(game.total_deaths, deaths_before)
        pygame.quit()

    def test_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            manager = SaveManager(path=__import__("pathlib").Path(path))
            data = SaveData()
            manager.push_record(data, "practice", 12.3, 4)
            manager.write(data)
            loaded = manager.load()
            self.assertEqual(loaded.leaderboard[0]["mode"], "practice")


if __name__ == "__main__":
    unittest.main()
