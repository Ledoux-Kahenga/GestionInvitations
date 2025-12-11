# 🎨 Guide de l'Éditeur de Template

## Vue d'ensemble

L'éditeur de template vous permet de positionner visuellement tous les éléments de vos invitations (nom, prénom, date, QR code, etc.) directement sur votre template.

## Comment utiliser l'éditeur

### 1. Ouvrir l'éditeur

Dans l'onglet **📅 Événements** :
1. Cliquez sur **📁 Template** pour choisir votre fichier template (PSD, PNG, JPG)
2. Cliquez sur **🎨 Éditer Template** pour ouvrir l'éditeur visuel

### 2. Interface de l'éditeur

L'éditeur se compose de deux panneaux :

#### Panneau gauche : Canvas de Design
- Affiche votre template
- Vous pouvez **glisser-déposer** les éléments pour les positionner
- Redimensionnez la fenêtre pour mieux voir

#### Panneau droit : Contrôles
- **Ajouter un élément** : Boutons pour ajouter différents champs
- **Propriétés** : Ajuster position, taille, police, couleur
- **Liste des éléments** : Voir tous les éléments ajoutés

### 3. Ajouter des éléments

Cliquez sur les boutons pour ajouter :

**Informations de l'invité :**
- `+ Nom Complet` : Prénom + Nom
- `+ Prénom` : Prénom uniquement
- `+ Nom` : Nom uniquement  
- `+ Catégorie` : VIP, Standard, Presse, etc.

**Informations de l'événement :**
- `+ Nom Événement` : Nom de l'événement
- `+ Date` : Date de l'événement
- `+ Heure` : Heure de l'événement
- `+ Lieu` : Lieu de l'événement

**QR Code :**
- `+ QR Code` : Code QR unique pour chaque invitation

### 4. Positionner les éléments

**Avec la souris :**
- Cliquez et maintenez sur un élément
- Déplacez-le à l'endroit souhaité
- Relâchez pour placer

**Avec les contrôles de précision :**
1. Cliquez sur un élément pour le sélectionner
2. Utilisez les champs du panneau "Propriétés" :
   - **Position X/Y** : Position exacte en pixels
   - **Largeur/Hauteur** : Taille de la zone
   - **Taille police** : Taille du texte
   - **Couleur** : Couleur du texte

### 5. Sauvegarder la configuration

1. Cliquez sur **💾 Sauvegarder Configuration**
2. La configuration est sauvegardée dans un fichier `.json` à côté de votre template
3. Cette configuration sera automatiquement utilisée lors de la génération des invitations

### 6. Générer les invitations

Une fois votre template configuré :
1. Allez dans l'onglet **👥 Invités** et ajoutez vos invités
2. Allez dans l'onglet **🎨 Générateur**
3. Sélectionnez votre événement
4. Cliquez sur **🎨 Générer toutes les invitations**

Les invitations seront générées avec vos positions personnalisées !

## Astuces

✅ **Prévisualisation** : Les éléments sur le canvas montrent où apparaîtront les informations

✅ **Zones transparentes** : Les rectangles bleus sont juste des guides, ils n'apparaîtront pas sur l'invitation finale

✅ **Superposition** : Vous pouvez superposer les éléments si nécessaire

✅ **Modification** : Vous pouvez rouvrir l'éditeur à tout moment pour ajuster les positions

✅ **Plusieurs templates** : Chaque template peut avoir sa propre configuration

## Fichiers générés

- **Template.png** → Votre fichier d'origine
- **Template.json** → Configuration des positions (créé automatiquement)
- **invitation_1.jpg** → Invitations générées (dans `invitations_generees/`)
- **qr_1.png** → QR codes individuels (dans `qrcodes/`)

## Exemple de workflow complet

1. 📁 Créez votre design dans Photoshop/GIMP et sauvegardez-le
2. 🎨 Ouvrez l'éditeur et positionnez les éléments
3. 💾 Sauvegardez la configuration
4. 📅 Créez votre événement et assignez le template
5. 👥 Ajoutez vos invités
6. 🎨 Générez toutes les invitations en un clic !

## Support des formats

- ✅ **PSD** (Photoshop) - Chargement direct sans Photoshop
- ✅ **PNG** - Transparence supportée
- ✅ **JPG/JPEG** - Format standard
- ✅ **Haute résolution** - 300 DPI par défaut

Bon design ! 🎨✨
