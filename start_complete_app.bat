@echo off
setlocal
cd /d "%~dp0"

echo ================================================
echo  Architect Advisor - Vista completa modulare
echo ================================================

if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>&1
    if not errorlevel 1 (py -3 -m venv .venv) else (python -m venv .venv)
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m streamlit run unified_app.py
endlocal
