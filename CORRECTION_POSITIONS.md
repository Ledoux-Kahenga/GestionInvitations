# 🔧 Correction des Positionnements - Documentation Technique

## 🐛 Problème identifié

Les positions définies dans l'éditeur ne correspondaient **pas** aux positions réelles sur les invitations générées.

### Causes principales :

1. **Dimensions originales non stockées pour les images JPG/PNG**
   - ❌ Seuls les fichiers PSD avaient leurs dimensions stockées
   - ❌ Pour JPG/PNG, `original_width` et `original_height` restaient à 0
   - ✅ **Corrigé** : Maintenant stockées pour tous les types

2. **Scale factor calculé sur le pixmap affiché, pas sur l'original**
   - ❌ Le calcul utilisait `self.template_pixmap.width()` (taille affichée)
   - ❌ Cela changeait à chaque redimensionnement de fenêtre
   - ✅ **Corrigé** : Utilise maintenant `self.original_width` (fixe)

3. **Canvas sans taille fixe**
   - ❌ Le canvas changeait de taille, affectant les positions
   - ✅ **Corrigé** : Taille fixée à `display_width x display_height`

## ✅ Solutions implémentées

### 1. Stockage cohérent des dimensions

**Avant :**
```python
# Seulement pour PSD
self.original_width = pil_image.width
self.original_height = pil_image.height

# Pour JPG/PNG -> rien ! ❌
```

**Après :**
```python
# Pour TOUS les types d'images
if str(image_path).lower().endswith('.psd'):
    # ... code PSD ...
    self.original_width = pil_image.width
    self.original_height = pil_image.height
else:
    self.template_pixmap = QPixmap(str(image_path))
    self.original_width = self.template_pixmap.width()  # ✅
    self.original_height = self.template_pixmap.height()  # ✅
```

### 2. Calcul correct du scale_factor

**Avant :**
```python
scale_w = available_width / self.template_pixmap.width()  # ❌ Taille affichée
scale_h = available_height / self.template_pixmap.height()  # ❌ Variable
```

**Après :**
```python
scale_w = available_width / self.original_width  # ✅ Taille réelle
scale_h = available_height / self.original_height  # ✅ Constante
```

### 3. Canvas à taille fixe

**Avant :**
```python
# Canvas redimensionnable -> positions changeantes ❌
```

**Après :**
```python
display_width = int(self.original_width * self.scale_factor)
display_height = int(self.original_height * self.scale_factor)
self.setFixedSize(display_width, display_height)  # ✅ Taille fixe
```

### 4. Debug complet ajouté

Maintenant, vous verrez dans la console :

```
🔄 Chargement du template: templates/MonTemplate.jpg
✅ Template chargé: 3000 x 2000 px
📐 Affichage: 900x600 (échelle: 0.300)
✅ Template chargé avec succès
   Dimensions originales: 3000 x 2000 px
   Échelle d'affichage: 0.300x
   Fichier config: templates/MonTemplate.json
```

Lors de l'ajout d'éléments :
```
➕ Ajout Nom Complet: position écran (350, 275) = réelle (1167, 917)
```

Lors de la sauvegarde :
```
💾 Configuration sauvegardée: templates/MonTemplate.json
   Template: 3000x2000
   Échelle: 0.300
   Éléments sauvegardés:
     - Nom Complet: (1167, 917) 600x80
     - QR Code: (2200, 1600) 400x400
```

## 🎯 Comment vérifier que ça fonctionne

### Test 1 : Vérifier les dimensions

1. Ouvrez l'éditeur de template
2. Chargez votre image
3. Vérifiez dans le panneau "Propriétés" :
   ```
   Template: 3000 x 2000 px  ← Dimensions réelles
   Échelle: 0.300x           ← Facteur d'affichage
   ```

### Test 2 : Positionner un élément

1. Ajoutez un élément (ex: Nom Complet)
2. Regardez le label sur l'élément : `Nom Complet (1167, 917)`
3. Ces coordonnées sont en **pixels réels**
4. Sélectionnez l'élément
5. Vérifiez les champs :
   - Position X (px réels) : 1167
   - Position Y (px réels) : 917

### Test 3 : Vérifier le fichier JSON

```json
{
  "template_path": "templates/MonTemplate.jpg",
  "template_width": 3000,      ← Doit correspondre à votre image
  "template_height": 2000,     ← Doit correspondre à votre image
  "scale_factor": 0.300,       ← Échelle d'affichage
  "elements": [
    {
      "id": "nom_complet",
      "x": 1167,                ← Position réelle X
      "y": 917,                 ← Position réelle Y
      "width": 600,             ← Largeur réelle
      "height": 80              ← Hauteur réelle
    }
  ]
}
```

### Test 4 : Générer une invitation

1. Générez une invitation test
2. Ouvrez l'image générée
3. Vérifiez que les éléments sont **exactement** où vous les avez positionnés
4. Les coordonnées dans la console doivent correspondre :
   ```
   ✅ Texte 'nom_complet' dessiné à (1167, 917)
   ✅ QR Code collé à (2200, 1600) taille 400x400
   ```

## 🔍 Script de diagnostic

Utilisez le script `verifier_positions.py` pour vérifier vos configurations :

```bash
python verifier_positions.py
```

Il affichera :
- Les dimensions du template
- La liste de tous les éléments avec leurs positions
- Les avertissements si quelque chose semble incorrect

## ⚠️ Si les positions ne correspondent toujours pas

### Solution 1 : Recréer la configuration

1. **Supprimez** le fichier `.json` à côté de votre template
2. **Rechargez** le template dans l'éditeur
3. **Repositionnez** tous les éléments
4. **Sauvegardez** à nouveau

### Solution 2 : Vérifier les dimensions de votre image

```python
from PIL import Image
img = Image.open("templates/MonTemplate.jpg")
print(f"Dimensions: {img.width} x {img.height}")
```

Ces dimensions doivent correspondre à `template_width` et `template_height` dans le JSON.

### Solution 3 : Vérifier les calculs

**Formule de conversion :**
```
Position écran = Position réelle × scale_factor
Position réelle = Position écran ÷ scale_factor
```

**Exemple :**
- Template : 3000 x 2000 px
- Affichage : 900 x 600 px
- Échelle : 900 / 3000 = 0.3

Si élément à X=350 sur écran :
- Position réelle : 350 / 0.3 = 1167 px

Si élément à X=1167 dans le JSON :
- Position écran : 1167 × 0.3 = 350 px

## 📊 Tableau de référence

| Template | Affichage | Échelle | Écran → Réel | Réel → Écran |
|----------|-----------|---------|--------------|--------------|
| 3000 px  | 900 px    | 0.300   | ÷ 0.300      | × 0.300      |
| 4000 px  | 800 px    | 0.200   | ÷ 0.200      | × 0.200      |
| 2000 px  | 1000 px   | 0.500   | ÷ 0.500      | × 0.500      |

## 🎓 Comprendre le système

```
┌─────────────────────────────────────────┐
│  TEMPLATE RÉEL (3000 x 2000 px)        │  ← Fichier sur disque
│                                         │
│  Element à (1500, 1000)                 │  ← Position réelle
│                                         │
└─────────────────────────────────────────┘
              ↓ × 0.3 (scale_factor)
┌─────────────────────────┐
│  AFFICHAGE (900 x 600)  │  ← Ce que vous voyez
│                         │
│  Element à (450, 300)   │  ← Position écran
│                         │
└─────────────────────────┘
```

**Important :** Les valeurs dans le JSON et dans les champs de l'éditeur sont **toujours en pixels réels**, pas en pixels d'affichage.

## ✅ Validation finale

Après les corrections, vous devriez avoir :
- ✅ Dimensions affichées correctement
- ✅ Échelle calculée correctement
- ✅ Positions en temps réel sur les éléments
- ✅ Sauvegarde avec les bonnes valeurs
- ✅ Génération d'invitations aux bonnes positions
- ✅ Messages de debug clairs dans la console

Si tout cela fonctionne, vos positionnements sont maintenant **parfaitement alignés** ! 🎯
