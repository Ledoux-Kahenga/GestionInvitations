# 🎨 Exemple d'utilisation des polices personnalisées

## Configuration d'exemple

Voici un exemple de configuration JSON avec une police personnalisée :

```json
{
  "template_path": "templates/MonInvitation.jpg",
  "template_width": 3000,
  "template_height": 2000,
  "scale_factor": 0.300,
  "elements": [
    {
      "id": "nom_complet",
      "label": "Nom Complet",
      "type": "text",
      "x": 1200,
      "y": 800,
      "width": 600,
      "height": 100,
      "font_size": 60,
      "font_name": "fonts/Elegant.ttf",
      "color": "#2C3E50"
    },
    {
      "id": "event_date",
      "label": "Date",
      "type": "text",
      "x": 1200,
      "y": 950,
      "width": 400,
      "height": 60,
      "font_size": 40,
      "font_name": "fonts/Modern.ttf",
      "color": "#E74C3C"
    },
    {
      "id": "event_lieu",
      "label": "Lieu",
      "type": "text",
      "x": 1200,
      "y": 1050,
      "width": 500,
      "height": 60,
      "font_size": 35,
      "font_name": "",
      "color": "#34495E"
    },
    {
      "id": "qrcode",
      "label": "QR Code",
      "type": "qr",
      "x": 2200,
      "y": 1600,
      "width": 400,
      "height": 400,
      "font_size": 40,
      "font_name": "",
      "color": "#000000"
    }
  ]
}
```

## Explication

### Élément 1 : Nom Complet
- **Police personnalisée** : `Elegant.ttf` pour un style élégant
- **Taille** : 60px pour bien ressortir
- **Couleur** : Bleu foncé (#2C3E50)

### Élément 2 : Date
- **Police personnalisée** : `Modern.ttf` pour un style moderne
- **Taille** : 40px
- **Couleur** : Rouge (#E74C3C) pour attirer l'attention

### Élément 3 : Lieu
- **Police par défaut** : `font_name` vide = police système
- **Taille** : 35px
- **Couleur** : Gris foncé (#34495E)

### Élément 4 : QR Code
- **Type** : qr (pas de police nécessaire)
- **Taille** : 400x400px

## Combinaisons de polices recommandées

### Classique & Élégant
```
Titres:     Playfair Display (60px, Bold)
Noms:       Cormorant Garamond (50px, Regular)
Texte:      Lato (35px, Regular)
```

### Moderne & Épuré
```
Titres:     Montserrat (70px, Bold)
Noms:       Raleway (55px, SemiBold)
Texte:      Open Sans (40px, Regular)
```

### Festif & Joyeux
```
Titres:     Pacifico (65px)
Noms:       Dancing Script (50px)
Texte:      Quicksand (38px)
```

### Professionnel
```
Titres:     Roboto Condensed (60px, Bold)
Noms:       Roboto (50px, Medium)
Texte:      Roboto (35px, Regular)
```

## Code pour tester

```python
from invitation_generator import InvitationGenerator

# Créer le générateur
gen = InvitationGenerator("templates/MonInvitation.jpg")

# Données de test
invite = {
    'id': 1,
    'nom': 'Dupont',
    'prenom': 'Marie',
    'categorie': 'VIP',
    'evenement': {
        'nom': 'Gala de Charité 2025',
        'date': '15 Décembre 2025',
        'heure': '19h00',
        'lieu': 'Grand Hotel Paris'
    }
}

# Générer l'invitation
path, qr = gen.creer_invitation(invite)
print(f"Invitation créée: {path}")
```

## Résultat attendu dans la console

```
✅ Template chargé: (3000, 2000)
✅ Configuration chargée: 4 éléments
✅ Police chargée: Elegant.ttf
✅ Texte 'nom_complet' dessiné à (1350, 825)
✅ Police chargée: Modern.ttf
✅ Texte 'event_date' dessiné à (1300, 965)
⚠️ Utilisation de la police par défaut
✅ Texte 'event_lieu' dessiné à (1250, 1065)
✅ QR Code collé à (2200, 1600) taille 400x400
```

## Astuces de design

1. **Limitez-vous à 2-3 polices différentes** maximum par invitation
2. **Utilisez une police décorative** uniquement pour les titres/noms
3. **Gardez le texte informatif lisible** avec une police simple
4. **Testez la lisibilité** : imprimez ou affichez en taille réelle
5. **Respectez la hiérarchie visuelle** :
   - Plus important = plus grand + police distinctive
   - Moins important = plus petit + police sobre

## Palette de couleurs harmonieuses

### Élégant
```
#2C3E50  (Bleu foncé)
#E74C3C  (Rouge)
#ECF0F1  (Blanc cassé)
#95A5A6  (Gris clair)
```

### Festif
```
#E91E63  (Rose vif)
#9C27B0  (Violet)
#FFC107  (Jaune or)
#4CAF50  (Vert)
```

### Professionnel
```
#263238  (Bleu gris foncé)
#546E7A  (Bleu gris)
#78909C  (Gris bleu)
#B0BEC5  (Gris clair)
```
