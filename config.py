"""
Configuration de l'application Gestion des Invitations
"""
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
INVITATIONS_DIR = BASE_DIR / "invitations_generees"
QRCODES_DIR = BASE_DIR / "qrcodes"
DATABASE_DIR = BASE_DIR / "database"
FONTS_DIR = BASE_DIR / "fonts"
DATABASE_PATH = DATABASE_DIR / "invitations.db"

# Créer les dossiers s'ils n'existent pas
for dir_path in [TEMPLATES_DIR, INVITATIONS_DIR, QRCODES_DIR, DATABASE_DIR, FONTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Polices par défaut
DEFAULT_FONTS = {
    'windows': ['arial.ttf', 'times.ttf', 'calibri.ttf', 'comic.ttf'],
    'linux': ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf']
}

# Configuration des invitations
INVITATION_CONFIG = {
    'format': 'A5',  # Format de l'invitation
    'dpi': 300,      # Résolution
    'quality': 95,   # Qualité JPEG
}

# Configuration QR Code
QR_CONFIG = {
    'version': 1,
    'box_size': 10,
    'border': 2,
    'error_correction': 'H',  # Haute correction d'erreur
}

# Couleurs de l'interface (identiques au projet Bureautique)
COLOR_PRIMARY = "#2E86AB"      # Bleu
COLOR_SUCCESS = "#06A77D"      # Vert
COLOR_DANGER = "#D62246"       # Rouge
COLOR_WARNING = "#F77F00"      # Orange
COLOR_SECONDARY = "#A23B72"    # Violet
COLOR_BACKGROUND = "#F5F5F5"   # Gris clair

# Informations de l'événement (par défaut)
EVENT_INFO = {
    'nom': "Nom de l'événement",
    'date': "JJ/MM/AAAA",
    'heure': "HH:MM",
    'lieu': "Adresse du lieu",
    'organisateur': "Nom de l'organisateur",
}
