@echo off
setlocal
cd /d "%~dp0"

echo ================================================
echo  AI Architect Advisor - Demo locale per Windows
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creazione ambiente virtuale...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3.12 -m venv .venv 2>nul
        if errorlevel 1 py -3 -m venv .venv
    ) else (
        where python >nul 2>&1
        if errorlevel 1 (
            echo ERRORE: Python 3.11 o superiore non trovato.
            echo Installa Python da https://www.python.org/downloads/
            pause
            exit /b 1
        )
        python -m venv .venv
    )
    if errorlevel 1 (
        echo ERRORE: impossibile creare l'ambiente virtuale.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente virtuale gia presente.
)

echo [2/3] Installazione dipendenze...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo ERRORE: installazione delle dipendenze non riuscita.
    pause
    exit /b 1
)

echo [3/3] Avvio della dashboard demo...
echo Per arrestare l'app premi CTRL+C in questa finestra.
".venv\Scripts\python.exe" -m streamlit run streamlit_app.py

endlocal
