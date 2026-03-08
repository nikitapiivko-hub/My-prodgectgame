# Neon Kolobok: Hell Tower

Хардкорная 2D-аркада для Windows 11 (и Linux/macOS для разработки) на **Python + Pygame**.

Игрок управляет неоновым колобком, поднимающимся по вертикальной адской башне. Ошибки наказываются мгновенно, но рестарт быстрый: фокус на ритме «ещё одна попытка».

## Особенности

- Оригинальная игра с собственным названием, стилем, логикой и структурой уровней.
- 3 режима:
  - **Normal** — редкий чекпоинт,
  - **Hardcore** — без чекпоинтов,
  - **Practice** — частые чекпоинты.
- Опасности: шипы, импульсные лазеры, исчезающие платформы, зоны ускорения.
- Вертикальная башня из 5 секций сложности (старт + 3 роста + финал).
- Эффекты: glow, trail, вспышка смерти, пульсации и shake.
- Локальное сохранение результатов и настроек в `save_data.json`.
- Локальный leaderboard (top-10).
- Поддержка 16:9, 60 FPS, переключение fullscreen (F11).

## Управление

- `A/D` или `←/→` — движение
- `Space` / `W` / `↑` — прыжок
- `R` — быстрый рестарт (смерть)
- `Esc` — пауза / возврат в меню
- `F11` — полноэкранный режим
- В меню:
  - `1` Normal
  - `2` Hardcore
  - `3` Practice
  - `M` музыка on/off
  - `N` sfx on/off

## Структура проекта

```text
.
├── assets/
├── build/
│   ├── build_windows.bat
│   └── build_windows.ps1
├── scripts/
│   └── run_local.sh
├── src/
│   └── neon_kolobok/
│       ├── audio.py
│       ├── game.py
│       ├── level.py
│       ├── main.py
│       ├── settings.py
│       └── storage.py
├── tests/
│   └── test_smoke.py
├── requirements.txt
├── run_game.py
└── README.md
```

## Быстрый запуск (локально)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src python run_game.py
```

или

```bash
bash scripts/run_local.sh
```

## Сборка Windows .exe

### Вариант 1 (cmd)

```bat
build\build_windows.bat
```

### Вариант 2 (PowerShell)

```powershell
./build/build_windows.ps1
```

Результат: `dist/NeonKolobokHellTower.exe`.

## Автопроверки / smoke tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

Проверяет:
- базовую загрузку уровня,
- столкновения/смерть,
- сохранение и чтение прогресса.

## Архитектура

- `game.py` — основной цикл, состояния (menu/playing/pause/win), рендер, эффекты, ввод.
- `level.py` — генерация башни и сущностей опасностей.
- `storage.py` — локальный persistence для рекордов и настроек.
- `audio.py` — процедурная генерация базовых звуков (без внешних ассетов).
- `main.py` / `run_game.py` — entrypoint запуска.

