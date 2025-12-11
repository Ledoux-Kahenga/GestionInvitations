# Gestion des Invitations avec QR Code

Application desktop PyQt5 pour la gestion d'événements avec génération d'invitations personnalisées et système de validation par QR code.

## 🌟 Fonctionnalités

### 📅 Gestion des Événements
- Créer et gérer des événements
- Définir date, heure, lieu, organisateur
- Associer un template d'invitation (PSD, PNG, JPG)

### 👥 Gestion des Invités
- Ajouter des invités par événement
- Catégorisation (Standard, VIP, Presse, Invité spécial)
- Gestion des accompagnants
- Informations de contact (email, téléphone)

### 🎨 Générateur d'Invitations
- Génération automatique à partir de templates
- Support des fichiers PSD (Photoshop) sans installation requise
- Personnalisation avec nom, catégorie, détails événement
- QR code unique par invité
- Export haute qualité (300 DPI, format A5)

### 📱 Scanner QR
- Scan en temps réel via webcam
- Validation instantanée des invitations
- Détection des doubles entrées
- Scan depuis fichier image
- Historique des scans avec horodatage

### 📊 Statistiques
- Nombre total d'invités et de personnes
- Taux de présence en temps réel
- Statistiques par catégorie
- Suivi des scans

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Caméra (pour le scanner QR)

### Installation des dépendances

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les packages
pip install -r requirements.txt
```

### Dépendances ZBar (pour le scanner QR)

**Ubuntu/Debian:**
```bash
sudo apt-get install libzbar0
```

**macOS:**
```bash
brew install zbar
```

**Windows:**
Télécharger depuis http://zbar.sourceforge.net/

## 🚀 Utilisation

### Lancer l'application

```bash
source .venv/bin/activate
python main.py
```

### Workflow typique

1. **Créer un événement**
   - Onglet "📅 Événements"
   - Remplir les informations
   - Sélectionner un template (optionnel)
   - Cliquer "Ajouter"

2. **Ajouter des invités**
   - Onglet "👥 Invités"
   - Sélectionner l'événement
   - Ajouter les invités un par un
   - Définir catégorie et nombre d'accompagnants

3. **Générer les invitations**
   - Onglet "🎨 Générateur"
   - Sélectionner l'événement
   - Cliquer "Générer toutes les invitations"
   - Les invitations sont créées dans `invitations_generees/`
   - Les QR codes dans `qrcodes/`

4. **Scanner les invitations**
   - Onglet "📱 Scanner"
   - Cliquer "Démarrer Scanner"
   - Présenter le QR code devant la caméra
   - Validation instantanée

5. **Consulter les statistiques**
   - Onglet "📊 Statistiques"
   - Voir le taux de présence en temps réel
   - Statistiques par catégorie

## 📁 Structure du Projet

```
GestionInvitations/
│
├── main.py                    # Application principale (interface GUI)
├── database_model.py          # Modèle de base de données SQLite
├── invitation_generator.py    # Générateur d'invitations
├── qr_scanner.py             # Scanner QR avec validation
├── config.py                 # Configuration
├── requirements.txt          # Dépendances
│
├── database/                 # Base de données SQLite
│   └── invitations.db
│
├── templates/                # Templates d'invitations (PSD/images)
│
├── invitations_generees/     # Invitations générées (JPG)
│
└── qrcodes/                  # QR codes générés (PNG)
```

## ⚙️ Configuration

Modifier `config.py` pour personnaliser:

- **Chemins**: Répertoires de travail
- **Format invitation**: Taille (A5), DPI (300), qualité (95)
- **QR Code**: Taille, correction d'erreur
- **Couleurs**: Thème de l'interface

## 🎨 Templates

### Créer un template

1. **Format recommandé**: A5 (1748x2480 pixels à 300 DPI)
2. **Formats supportés**: PSD, PNG, JPG
3. **Zone QR**: Réserver espace en bas à droite (400x400px)

### Utilisation sans template

L'application génère automatiquement un template blanc si aucun n'est fourni.

## 📊 Base de Données

### Tables

- **evenements**: Informations sur les événements
- **invites**: Liste des invités avec QR codes
- **scans**: Historique des scans QR

### Sauvegarde

La base de données est dans `database/invitations.db`. Sauvegarder ce fichier pour conserver toutes les données.

## 🔒 Sécurité

- QR codes uniques et non prédictibles (UUID)
- Vérification contre les doubles scans
- Correction d'erreur élevée (niveau H) pour les QR codes
- Validation en temps réel contre la base de données

## 🐛 Dépannage

### Le scanner ne détecte pas la caméra
```bash
# Vérifier les caméras disponibles
ls /dev/video*

# Tester avec un autre index de caméra
# Modifier camera_index dans qr_scanner.py
```

### Erreur d'importation de pyzbar
```bash
# Installer libzbar
sudo apt-get install libzbar0  # Ubuntu/Debian
```

### Les PSD ne se chargent pas
```bash
# Vérifier l'installation de psd-tools
pip install --upgrade psd-tools
```

## 📝 Exemples

### Générer une invitation manuellement

```python
from invitation_generator import InvitationGenerator

generator = InvitationGenerator("templates/mon_template.psd")

invite_data = {
    'id': 1,
    'nom': 'Dupont',
    'prenom': 'Jean',
    'categorie': 'VIP',
    'evenement': {
        'nom': 'Gala de Charité',
        'date': '2025-12-31',
        'heure': '19:00',
        'lieu': 'Grand Hôtel'
    }
}

path, qr_code = generator.creer_invitation(invite_data)
print(f"Invitation générée: {path}")
print(f"QR Code: {qr_code}")
```

### Scanner un QR code

```python
from qr_scanner import QRScanner

scanner = QRScanner()
validation = scanner.scanner_fichier_image("invitation.jpg")

if validation['valide']:
    print(f"✅ {validation['message']}")
    print(f"Invité: {validation['invite']['nom']}")
else:
    print(f"❌ {validation['message']}")
```

## 🚀 Améliorations Futures

- [ ] Export Excel des listes d'invités
- [ ] Import CSV pour ajout en masse
- [ ] Envoi automatique par email
- [ ] Templates multiples par événement
- [ ] Rapports PDF détaillés
- [ ] Support multi-langue
- [ ] API REST pour intégration mobile
- [ ] Notifications push

## 📜 Licence

MIT

## 👨‍💻 Auteur

Développé avec ❤️ pour simplifier la gestion d'événements

## 🆘 Support

Pour toute question ou problème, ouvrir une issue sur le dépôt.
