from __future__ import annotations

import math
import struct

import pygame


def _tone(frequency: float, duration: float, volume: float = 0.4, sample_rate: int = 44100) -> bytes:
    samples = int(duration * sample_rate)
    buf = bytearray()
    attack = int(samples * 0.1)
    release = int(samples * 0.25)
    for i in range(samples):
        env = 1.0
        if i < attack:
            env = i / max(attack, 1)
        elif i > samples - release:
            env = max(0.0, (samples - i) / max(release, 1))
        value = math.sin(2 * math.pi * frequency * i / sample_rate)
        value += 0.3 * math.sin(2 * math.pi * (frequency * 2.01) * i / sample_rate)
        sample = int(32767 * volume * env * value)
        buf.extend(struct.pack("<h", max(-32768, min(32767, sample))))
    return bytes(buf)


class AudioBank:
    def __init__(self, sfx_volume: float, music_volume: float) -> None:
        self.ready = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.jump = pygame.mixer.Sound(buffer=_tone(520, 0.12, sfx_volume))
            self.death = pygame.mixer.Sound(buffer=_tone(130, 0.3, sfx_volume))
            self.menu = pygame.mixer.Sound(buffer=_tone(760, 0.06, sfx_volume))
            self.ambient = pygame.mixer.Sound(buffer=_tone(70, 1.6, music_volume * 0.45))
        except pygame.error:
            self.ready = False

    def play_ambient(self) -> None:
        if self.ready:
            self.ambient.play(loops=-1)

    def stop_ambient(self) -> None:
        if self.ready:
            self.ambient.stop()
