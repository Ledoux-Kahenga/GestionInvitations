@echo off
REM Script d'installation des dépendances pour Windows

echo Installation des dependances...
echo.

REM Installer les dépendances
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Installation terminee!
echo.
echo Pour lancer l'application, executez: run.bat
pause
