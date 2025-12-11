# Guide de Positionnement des Éléments

## 🎯 Comprendre le système de coordonnées

### Dimensions et échelle

Votre template d'invitation a des **dimensions réelles** (par exemple 3000x2000 pixels).
L'éditeur affiche une version **réduite** à l'écran pour que tout soit visible.

**Exemple :**
- Template réel : 3000 x 2000 pixels
- Affichage écran : 900 x 600 pixels
- Échelle : 0.30x (30% de la taille réelle)

### 📍 Système de coordonnées

```
(0, 0) ─────────────────► X
  │
  │    [Votre Template]
  │
  │
  ▼
  Y
```

- **Position X** : Distance depuis le bord **gauche** (en pixels réels)
- **Position Y** : Distance depuis le bord **haut** (en pixels réels)
- **Largeur** : Largeur de la zone (en pixels réels)
- **Hauteur** : Hauteur de la zone (en pixels réels)

## 🎨 Utilisation de l'éditeur

### 1. Charger un template

1. Cliquez sur **"📂 Charger Template"**
2. Sélectionnez votre image (JPG, PNG, ou PSD)
3. Notez les **dimensions affichées** :
   ```
   Template: 3000 x 2000 px
   Échelle: 0.30x
   ```

### 2. Ajouter des éléments

Cliquez sur les boutons pour ajouter des éléments :
- **Texte** : Nom Complet, Date, Lieu, etc.
- **QR Code** : Code de scan pour l'invité

Chaque élément apparaît au **centre du canvas**.

### 3. Positionner les éléments

**Deux méthodes :**

#### A. Déplacement à la souris (recommandé)
1. Cliquez et **maintenez** sur l'élément
2. **Déplacez** vers la position souhaitée
3. Les coordonnées s'affichent **en temps réel** sur l'élément
4. Relâchez pour fixer la position

#### B. Saisie manuelle
1. **Sélectionnez** l'élément en cliquant dessus
2. Utilisez les champs dans le panneau **"Propriétés"** :
   - **Position X (px réels)** : Position horizontale
   - **Position Y (px réels)** : Position verticale
   - **Largeur (px réels)** : Largeur de la zone
   - **Hauteur (px réels)** : Hauteur de la zone

### 4. Ajuster la taille

Pour redimensionner un élément :
1. **Sélectionnez** l'élément
2. Modifiez **Largeur** et **Hauteur** dans les propriétés
3. La taille change instantanément

### 5. Sauvegarder la configuration

1. Cliquez sur **"💾 Sauvegarder Config"**
2. Un fichier `.json` est créé à côté de votre template
3. Cette configuration sera utilisée pour générer les invitations

## ⚠️ Problèmes courants et solutions

### ❌ "Les éléments sont mal positionnés sur l'invitation finale"

**Cause :** Les coordonnées sauvegardées ne correspondent pas aux positions réelles.

**Solution :**
1. Rechargez le template dans l'éditeur
2. Vérifiez l'**échelle affichée**
3. Repositionnez les éléments
4. **Sauvegardez à nouveau** la configuration

### ❌ "Le QR code est trop petit ou trop grand"

**Cause :** La hauteur et largeur ne sont pas carrées.

**Solution :**
1. Sélectionnez le QR code
2. Mettez la **même valeur** pour Largeur et Hauteur
3. Exemple : 500 x 500 px pour un grand QR code

### ❌ "Le texte dépasse de la zone"

**Cause :** La zone de texte est trop petite.

**Solution :**
1. Augmentez la **Largeur** de la zone
2. Augmentez la **Hauteur** si nécessaire
3. Réduisez la **Taille police** si le texte reste trop grand

### ❌ "Je ne vois pas l'élément sur le canvas"

**Cause :** L'élément est positionné hors limites.

**Solution :**
1. Sélectionnez l'élément dans la liste
2. Mettez **Position X = 100** et **Position Y = 100**
3. L'élément reviendra dans la zone visible

## 📐 Conseils pratiques

### ✅ Bonnes pratiques

1. **Commencez par le centre** : Les éléments apparaissent au centre, c'est un bon point de départ

2. **Utilisez la souris pour le placement grossier** : Rapide et intuitif

3. **Affinez avec les champs numériques** : Pour une précision au pixel près

4. **Testez avec l'aperçu** : Vérifiez le rendu avant de générer toutes les invitations

5. **Notez les valeurs** : Si vous avez plusieurs templates similaires, gardez une trace des positions qui fonctionnent bien

### 📏 Dimensions recommandées

**Pour le texte :**
- Nom : 400-600 px de large, 60-80 px de haut
- Date/Lieu : 300-400 px de large, 40-50 px de haut
- Taille police : 30-60 pour le texte normal, 60-100 pour les titres

**Pour le QR Code :**
- Minimum : 200 x 200 px
- Recommandé : 400 x 400 px
- Maximum : 600 x 600 px

### 🎯 Positionnement harmonieux

**Règle des tiers :**
- Divisez mentalement votre template en 3x3
- Placez les éléments importants aux intersections
- Laissez de l'espace (respiration)

**Marges :**
- Gardez au moins 100-150 px de marge sur les bords
- Évitez de coller les éléments aux bords

## 🔧 Informations techniques

### Format du fichier de configuration (.json)

```json
{
  "template_path": "chemin/vers/template.jpg",
  "template_width": 3000,
  "template_height": 2000,
  "scale_factor": 0.3,
  "elements": [
    {
      "id": "nom_complet",
      "label": "Nom Complet",
      "type": "text",
      "x": 1200,
      "y": 800,
      "width": 600,
      "height": 80,
      "font_size": 50,
      "color": "#000000"
    }
  ]
}
```

### Variables disponibles

**Pour le texte :**
- `nom_complet` : Prénom + Nom
- `prenom` : Prénom uniquement
- `nom` : Nom uniquement
- `categorie` : Catégorie de l'invité (VIP, Standard, etc.)
- `event_nom` : Nom de l'événement
- `event_date` : Date de l'événement
- `event_heure` : Heure de l'événement
- `event_lieu` : Lieu de l'événement

**Pour le QR Code :**
- `qrcode` : Code QR unique généré automatiquement

## 📞 Besoin d'aide ?

Si les positions restent bizarres :
1. Vérifiez que le fichier `.json` est à côté du template
2. Supprimez le fichier `.json` et recommencez
3. Utilisez un template plus petit (maximum 4000x3000 px)
4. Vérifiez que les valeurs X, Y, Width, Height sont raisonnables (pas de valeurs négatives ou énormes)
