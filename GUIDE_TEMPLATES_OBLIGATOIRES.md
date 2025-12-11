# 🖼️ Gestion des Templates d'Événements

## ⚠️ Règles importantes

### Template obligatoire
Un **template d'invitation est maintenant OBLIGATOIRE** pour créer un événement.

Sans template → ❌ **Impossible de créer l'événement**

## 📋 Création d'un événement

### Étape par étape

#### 1. Remplir les informations de base
```
✏️ Nom de l'événement : "Gala 2025"
📅 Date : 15/12/2025
🕐 Heure : 19:00
📍 Lieu : "Grand Hotel"
👤 Organisateur : "Association XYZ"
```

#### 2. **OBLIGATOIRE** : Choisir un template
- Cliquez sur **📁 Choisir Template**
- Sélectionnez une image (JPG, PNG, PSD)
- Le label affiche : **✅ NomDuFichier.jpg** (vert)

#### 3. (Optionnel) Éditer le template
- Cliquez sur **🎨 Éditer**
- Positionnez les éléments (nom, date, QR code, etc.)
- Sauvegardez la configuration

#### 4. Créer l'événement
- Cliquez sur **➕ Ajouter**
- L'événement est créé avec son template

### ❌ Si vous oubliez le template

Vous verrez ce message :
```
⚠️ Un template d'invitation est obligatoire!

Veuillez cliquer sur '📁 Choisir Template' 
pour sélectionner une image.
```

## 🔄 Modification d'un événement existant

### Modifier les informations ET l'image

#### 1. Sélectionner l'événement
- Cliquez sur l'événement dans le tableau
- Cliquez sur **✏️ Modifier l'événement sélectionné**

#### 2. Le formulaire se remplit
```
Nom : "Gala 2025"
Date : 15/12/2025
...
Template : ✅ AncienTemplate.jpg (vert)
```

#### 3. Modifier ce que vous voulez
- **Changer le nom** : Modifiez le champ
- **Changer la date** : Sélectionnez une nouvelle date
- **Changer le template** : 
  - Cliquez sur **📁 Choisir Template**
  - Sélectionnez une nouvelle image
  - Le label se met à jour : **✅ NouveauTemplate.jpg**

#### 4. Sauvegarder
- Cliquez sur **➕ Ajouter**
- Toutes les modifications sont enregistrées

### ✨ Vous pouvez changer l'image !

Même pour un événement existant, vous pouvez :
- Choisir un nouveau template
- Éditer le nouveau template
- Tout est mis à jour

## 🎨 Indicateurs visuels

### Label du template

#### Aucun template sélectionné
```
❌ Aucun template
```
- Couleur : **Rouge**
- Signification : **Obligatoire, manquant**

#### Template sélectionné
```
✅ MonInvitation.jpg
```
- Couleur : **Vert**
- Signification : **OK, template valide**

### Boutons

#### 📁 Choisir Template
- Fond bleu
- Toujours actif
- Permet de sélectionner/changer le template

#### 🎨 Éditer
- Gris (par défaut)
- **Nécessite un template sélectionné**
- Ouvre l'éditeur de positionnement

## 🔍 Scénarios d'utilisation

### Scénario 1 : Nouvel événement

```
1. Remplir "Nom de l'événement"
2. Cliquer "📁 Choisir Template"
   → Label : ✅ Template.jpg (vert)
3. Optionnel : Cliquer "🎨 Éditer"
4. Cliquer "➕ Ajouter"
   → ✅ Événement créé !
```

### Scénario 2 : Oublier le template

```
1. Remplir "Nom de l'événement"
2. Ne PAS choisir de template
   → Label : ❌ Aucun template (rouge)
3. Cliquer "➕ Ajouter"
   → ⚠️ Message d'erreur
   → ❌ Événement NON créé
```

### Scénario 3 : Modifier l'image d'un événement

```
1. Sélectionner événement dans le tableau
2. Cliquer "✏️ Modifier l'événement sélectionné"
   → Formulaire rempli
   → Label : ✅ AncienTemplate.jpg
3. Cliquer "📁 Choisir Template"
4. Sélectionner nouveau fichier
   → Label : ✅ NouveauTemplate.jpg
5. Cliquer "➕ Ajouter"
   → ✅ Image mise à jour !
```

### Scénario 4 : Éditer sans template

```
1. Nouveau formulaire vide
   → Label : ❌ Aucun template
2. Cliquer "🎨 Éditer"
   → ⚠️ Message : "Veuillez d'abord sélectionner un template!"
   → ❌ Éditeur ne s'ouvre pas
```

## 📊 Tableau de synthèse

| Action | Template requis ? | Résultat |
|--------|-------------------|----------|
| Créer événement | ✅ OUI | Sans template = Erreur |
| Modifier événement | ✅ OUI | Peut changer le template |
| Éditer template | ✅ OUI | Doit être sélectionné d'abord |
| Choisir template | ❌ NON | Toujours disponible |

## 🎯 Workflow complet recommandé

### Pour un nouvel événement avec personnalisation

```
1️⃣ Choisir template
   📁 Choisir Template → Sélectionner image

2️⃣ Éditer le template
   🎨 Éditer → Positionner éléments → 💾 Sauvegarder

3️⃣ Remplir les informations
   ✏️ Nom, Date, Heure, Lieu, Organisateur

4️⃣ Créer l'événement
   ➕ Ajouter

5️⃣ Générer les invitations
   🎨 Générateur → Sélectionner invités → Générer
```

## 🔧 Messages d'erreur

### "Template requis"
```
⚠️ Un template d'invitation est obligatoire!

Veuillez cliquer sur '📁 Choisir Template' 
pour sélectionner une image.
```
**Solution** : Choisissez un template avant de créer l'événement.

### "Aucun template"
```
⚠️ Veuillez d'abord sélectionner un template!

Cliquez sur '📁 Choisir Template' 
pour sélectionner une image.
```
**Solution** : Choisissez un template avant d'éditer.

## 💡 Conseils pratiques

### Pour économiser du temps
1. **Créez des templates réutilisables** dans le dossier `templates/`
2. **Configurez-les une fois** avec l'éditeur
3. **Réutilisez-les** pour plusieurs événements similaires

### Pour les événements similaires
- Utilisez le **même template** pour plusieurs événements
- La configuration (positions des éléments) est liée au template
- Changez juste les informations (nom, date, lieu)

### Pour changer de style
- En mode modification, **choisissez un nouveau template**
- Vous pouvez même **passer d'une image à une autre**
- Toutes les invitations futures utiliseront le nouveau template

## 🎨 Exemples pratiques

### Exemple 1 : Gala annuel
```
Année 2024 : Template "Gala2024.jpg"
Année 2025 : Modifier l'événement → Nouveau template "Gala2025.jpg"
→ Design mis à jour !
```

### Exemple 2 : Plusieurs événements, même style
```
Événement 1 : "Conférence Matin" → Template "Conference.jpg"
Événement 2 : "Conférence Soir" → Template "Conference.jpg"
→ Même design, infos différentes !
```

## 🚀 Résumé des améliorations

### ✅ Ce qui a changé
- Template **obligatoire** pour créer un événement
- **Impossible** de créer sans template
- Possibilité de **changer le template** lors de la modification
- **Indicateur visuel** clair (rouge/vert)
- **Messages d'erreur** explicites

### 🎯 Pourquoi c'est mieux
- ✅ Garantit que chaque événement a une invitation
- ✅ Évite les erreurs lors de la génération
- ✅ Plus intuitif avec les indicateurs visuels
- ✅ Flexible : on peut changer le template après
- ✅ Professionnel : design cohérent

Profitez de ce système amélioré pour gérer vos événements ! 🎉
