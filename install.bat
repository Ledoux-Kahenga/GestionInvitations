@echo off
REM Script d'installation des dépendances pour Windows

echo Installation des dependances...
echo.

REM Creer l'environnement virtuel avec Python 3.11
py -3.11 -m venv .venv
if errorlevel 1 (
    echo.
    echo Erreur: Python 3.11 est requis pour installer ce projet.
    echo Installez Python 3.11 puis relancez install.bat.
    pause
    exit /b 1
)

REM Installer les dependances dans l'environnement virtuel
".venv\Scripts\python.exe" -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --timeout 120 -r requirements.txt
if errorlevel 1 (
    echo.
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo Installation terminee!
echo.
echo Pour lancer l'application, executez: run.bat
pause
