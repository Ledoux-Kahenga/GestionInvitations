@echo off
REM Script de lancement de l'application pour Windows

REM Désactiver les dialogues natifs
set QT_FILE_DIALOG_USE_NATIVE=0

REM Se déplacer dans le dossier du script
cd /d "%~dp0"

REM Lancer l'application
python main.py %*
