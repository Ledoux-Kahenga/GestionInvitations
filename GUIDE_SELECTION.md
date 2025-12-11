# 🎯 Guide du Système de Sélection et Modification des Styles

## 🖱️ Comment sélectionner un élément

### Méthode 1 : Cliquer sur le canvas
1. **Cliquez** directement sur un élément dans la zone de design
2. L'élément devient **rouge** pour indiquer qu'il est sélectionné
3. Les propriétés s'affichent automatiquement dans le panneau de droite

### Méthode 2 : Cliquer dans la liste
1. Dans le panneau **"Éléments ajoutés"** à droite
2. **Cliquez** sur le nom de l'élément que vous voulez modifier
3. L'élément sur le canvas devient **rouge** et sélectionné

## 🎨 Modification des styles en temps réel

Une fois qu'un élément est **sélectionné** (rouge), vous pouvez modifier :

### 📍 Position et Taille
- **Position X** : Déplace l'élément horizontalement (pixels réels)
- **Position Y** : Déplace l'élément verticalement (pixels réels)
- **Largeur** : Change la largeur de la zone
- **Hauteur** : Change la hauteur de la zone

💡 **Astuce** : Les changements sont **instantanés** !

### 🔤 Style du texte

#### Taille de la police
- Utilisez le champ **"Taille police"**
- Plage : 10 à 200 pixels
- Le changement s'applique **immédiatement**

#### Police
1. Ouvrez le menu déroulant **"Police"**
2. Choisissez parmi :
   - Police par défaut
   - Vos polices personnalisées
   - Polices système
3. La police est appliquée **instantanément**

#### Couleur
1. Cliquez sur **"Choisir couleur"**
2. Sélectionnez une couleur dans le sélecteur
3. Validez
4. Le bouton prend la couleur sélectionnée

## 🔄 Indicateurs visuels

### États des éléments

#### Non sélectionné (Bleu)
```
┌─────────────────────┐
│  Élément Normal     │ ← Bordure bleue en pointillés
│  (1200, 800)        │ ← Fond bleu transparent
└─────────────────────┘
```

#### Sélectionné (Rouge)
```
┏━━━━━━━━━━━━━━━━━━━━━┓
┃  Élément Sélectionné┃ ← Bordure rouge solide
┃  (1200, 800)        ┃ ← Fond rouge transparent
┗━━━━━━━━━━━━━━━━━━━━━┛
```

### Console de debug

Lors des modifications, vous verrez dans la console :

```
✓ Élément sélectionné: Nom Complet
✓ Taille police: 60px
✓ Police changée: Elegant.ttf
✓ Couleur changée: #E74C3C
```

## 🎯 Workflow typique

### 1. Ajouter un élément
```
Cliquer sur "+ Nom Complet" → Élément apparaît au centre
```

### 2. Positionner (optionnel)
```
Glisser-déposer l'élément → Position mise à jour automatiquement
```

### 3. Sélectionner
```
Cliquer sur l'élément → Devient rouge
```

### 4. Personnaliser le style
```
Panneau Propriétés:
├─ Taille police: 60
├─ Police: Elegant.ttf
└─ Couleur: Rouge (#E74C3C)
```

### 5. Ajuster position précise
```
Position X: 1200
Position Y: 800
Largeur: 600
Hauteur: 100
```

### 6. Sauvegarder
```
Cliquer sur "💾 Sauvegarder Config"
```

## 💡 Astuces pratiques

### Basculer entre les éléments
- Cliquez sur un élément dans la liste pour passer rapidement de l'un à l'autre
- L'élément précédent redevient bleu, le nouveau devient rouge

### Modifier plusieurs propriétés
1. Sélectionnez l'élément **une seule fois**
2. Modifiez **autant de propriétés** que vous voulez
3. Tous les changements sont appliqués **en temps réel**

### Vérifier l'élément sélectionné
- **Couleur rouge** = Élément sélectionné
- **Couleur bleue** = Élément non sélectionné

### Annuler une sélection
- Cliquez sur un autre élément
- Ou cliquez sur une zone vide du canvas (si implémenté)

## 🎨 Exemple pratique : Personnaliser un nom

### Avant
```
┌─────────────────────┐
│  Nom Complet        │ ← Bleu, 40px, Arial
│  (1200, 800)        │
└─────────────────────┘
```

### Étapes
1. **Clic** sur l'élément → Devient rouge
2. **Taille police**: Changer à 60
3. **Police**: Sélectionner "Dancing Script"
4. **Couleur**: Choisir or (#FFD700)
5. **Position Y**: Ajuster à 850

### Après
```
┏━━━━━━━━━━━━━━━━━━━━━┓
┃  Nom Complet        ┃ ← Rouge (sélectionné)
┃  (1200, 850)        ┃ ← 60px, Dancing Script, Or
┗━━━━━━━━━━━━━━━━━━━━━┛
```

## 🔍 Comparaison : Avant / Après

### ❌ Avant (système ancien)
- Il fallait re-cliquer pour chaque modification
- Pas d'indicateur visuel clair
- Difficile de savoir quel élément était actif
- Liste statique non interactive

### ✅ Après (système amélioré)
- Sélection une fois, modification multiple
- **Indicateur rouge** très visible
- Liste **interactive** et cliquable
- Bouton couleur montre la **couleur actuelle**
- Messages de **confirmation** dans la console

## 🎯 Raccourcis et fonctionnalités

| Action | Comment |
|--------|---------|
| Sélectionner | Clic sur l'élément (canvas ou liste) |
| Déplacer | Glisser-déposer (reste sélectionné) |
| Position précise | Champs X, Y |
| Taille | Champs Largeur, Hauteur |
| Police | Menu déroulant + bouton 📁 |
| Taille texte | SpinBox (10-200) |
| Couleur | Bouton "Choisir couleur" |
| Désélectionner | Cliquer sur autre élément |

## ⚡ Performance

Le système est optimisé pour :
- ✅ **Bloquer les signaux** pendant la mise à jour (pas de boucles infinies)
- ✅ **Mise à jour instantanée** de l'interface
- ✅ **Pas de rechargement** nécessaire
- ✅ **Feedback visuel immédiat**

## 🐛 Dépannage

### L'élément ne change pas de couleur
- Vérifiez que vous avez bien **cliqué** sur l'élément
- L'élément doit devenir **rouge**
- Si problème, cliquez dans la liste à droite

### Les modifications ne s'appliquent pas
- Vérifiez qu'un élément est **sélectionné** (rouge)
- Vérifiez la console pour les messages d'erreur

### Je ne vois pas l'élément dans la liste
- Vérifiez que vous avez bien **ajouté** l'élément
- La liste se met à jour automatiquement

### La couleur du bouton ne change pas
- C'est normal si aucun élément n'est sélectionné
- Sélectionnez d'abord un élément de **type texte**

## 📊 Récapitulatif des couleurs

### États visuels
- 🔵 **Bleu** = Non sélectionné (disponible)
- 🔴 **Rouge** = Sélectionné (en cours d'édition)
- ⚪ **Blanc** = Bouton de liste (au repos)
- 🔵 **Bleu clair** = Bouton de liste (survol)

### Exemple de session
```
1. Ajouter "Nom Complet"          → Bleu
2. Cliquer dessus                 → Rouge
3. Modifier taille: 60            → Toujours rouge
4. Modifier couleur: Or           → Toujours rouge
5. Cliquer sur "Date"             → "Nom" redevient bleu
6. "Date" devient rouge           → On modifie "Date"
```

## ✨ Nouvelles fonctionnalités

### Liste interactive
- ✅ Boutons cliquables pour chaque élément
- ✅ Survol avec changement de couleur
- ✅ Scroll si beaucoup d'éléments

### Indicateurs visuels
- ✅ Bordure rouge épaisse pour la sélection
- ✅ Bouton couleur avec aperçu
- ✅ Messages dans la console

### Modifications en temps réel
- ✅ Taille de police
- ✅ Choix de police
- ✅ Couleur du texte
- ✅ Position et dimensions

Profitez de ce système amélioré pour créer des invitations magnifiques ! 🎨✨
