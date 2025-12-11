#!/bin/bash
# Script de lancement de l'application avec configuration pour éviter les crashs

# Désactiver les dialogues natifs
export QT_FILE_DIALOG_USE_NATIVE=0

# Lancer l'application
cd "$(dirname "$0")"
.venv/bin/python main.py "$@"
