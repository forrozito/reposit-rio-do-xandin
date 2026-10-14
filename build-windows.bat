@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onefile --windowed --name ConsultorioDental app.py
if errorlevel 1 exit /b 1
echo Aplicativo criado em dist\ConsultorioDental.exe
