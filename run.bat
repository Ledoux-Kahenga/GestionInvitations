@echo off
REM Script de lancement de l'application pour Windows

REM Désactiver les dialogues natifs
set QT_FILE_DIALOG_USE_NATIVE=0

REM Se déplacer dans le dossier du script
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Environnement virtuel introuvable.
    echo Lancez install.bat avant de demarrer l'application.
    pause
    exit /b 1
)

REM Lancer l'application
".venv\Scripts\python.exe" main_modern.py %*
