$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --noconfirm --clean --onefile --name "NeonKolobokHellTower" --paths src run_game.py
Write-Host "Build completed. EXE: dist/NeonKolobokHellTower.exe"
