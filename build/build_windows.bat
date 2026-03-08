@echo off
setlocal

if not exist .venv (
  py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --noconfirm --clean --onefile --name "NeonKolobokHellTower" --paths src run_game.py

echo Build completed. EXE: dist\NeonKolobokHellTower.exe
endlocal
