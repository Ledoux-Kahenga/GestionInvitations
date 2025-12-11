# 📝 Gestion des Polices Personnalisées

## 🎨 Comment ajouter des polices

### Méthode 1 : Via l'éditeur de template (recommandée)

1. Ouvrez l'éditeur de template (🎨 Éditer Template)
2. Sélectionnez un élément de texte
3. Dans le panneau "Propriétés", cherchez le champ "Police:"
4. Cliquez sur le bouton **📁** à côté du menu déroulant
5. Sélectionnez votre fichier de police (.ttf ou .otf)
6. La police est automatiquement copiée dans le dossier `fonts/`

### Méthode 2 : Manuellement

1. Copiez vos fichiers de police (.ttf ou .otf) dans le dossier `fonts/`
2. Relancez l'application
3. Les polices apparaîtront dans le menu déroulant

## 📂 Structure

```
GestionInvitations/
├── fonts/                    ← Placez vos polices ici
│   ├── MaPolice1.ttf
│   ├── MaPolice2.ttf
│   └── ...
├── templates/
├── invitations_generees/
└── ...
```

## 🔤 Polices disponibles par défaut

L'application utilise automatiquement les polices système :

### Windows
- Arial
- Times New Roman
- Calibri
- Comic Sans MS
- Georgia
- Verdana
- Tahoma

### Linux
- DejaVu Sans
- DejaVu Sans Bold
- Liberation Sans

## 🎯 Utilisation dans l'éditeur

1. **Sélectionnez un élément de texte** (Nom, Prénom, Date, etc.)
2. Dans le panneau **"Propriétés"** :
   - **Police:** Choisissez la police dans le menu déroulant
   - **Taille police:** Ajustez la taille (10-200)
   - **Couleur:** Cliquez pour choisir une couleur
3. **Sauvegardez** la configuration (💾)

## 📄 Formats supportés

- **.ttf** - TrueType Font (recommandé)
- **.otf** - OpenType Font

## ⚙️ Configuration technique

Les informations de police sont sauvegardées dans le fichier `.json` à côté de votre template :

```json
{
  "elements": [
    {
      "id": "nom_complet",
      "type": "text",
      "font_size": 50,
      "font_name": "C:\\Projets\\GestionInvitations\\fonts\\MaPolice.ttf",
      "color": "#000000"
    }
  ]
}
```

## 💡 Conseils

### Pour un rendu optimal :

1. **Utilisez des polices lisibles** pour les noms et informations importantes
2. **Taille minimale recommandée :** 30-40 pour le texte normal
3. **Taille pour les titres :** 60-100
4. **Évitez les polices trop fantaisistes** pour les informations critiques
5. **Testez le rendu** avec l'aperçu avant de générer toutes les invitations

### Polices recommandées :

**Pour les noms (élégant) :**
- Playfair Display
- Cormorant
- Great Vibes
- Dancing Script

**Pour le texte (lisible) :**
- Roboto
- Open Sans
- Lato
- Montserrat

**Pour les titres (impactant) :**
- Bebas Neue
- Oswald
- Raleway Bold
- Poppins Bold

## 🌐 Où trouver des polices gratuites

- **Google Fonts** : https://fonts.google.com/
- **DaFont** : https://www.dafont.com/
- **Font Squirrel** : https://www.fontsquirrel.com/
- **1001 Fonts** : https://www.1001fonts.com/

⚠️ **Attention aux licences** : Vérifiez que vous avez le droit d'utiliser la police pour un usage commercial si nécessaire.

## 🐛 Dépannage

### La police ne s'affiche pas dans la liste

1. Vérifiez que le fichier est bien dans le dossier `fonts/`
2. Vérifiez l'extension (.ttf ou .otf)
3. Relancez l'application

### La police s'affiche mal sur l'invitation

1. Vérifiez que le fichier de police n'est pas corrompu
2. Essayez avec une taille de police différente
3. Vérifiez que la zone de texte est assez grande

### "Erreur chargement police"

1. Le fichier de police existe-t-il toujours ?
2. Avez-vous les droits de lecture sur le fichier ?
3. Essayez de supprimer et réajouter la police

### La police par défaut est utilisée

Cela arrive quand :
- Le chemin de la police dans le JSON est incorrect
- Le fichier de police a été supprimé ou déplacé
- La police est corrompue

**Solution :** Rechargez le template dans l'éditeur, resélectionnez la police, et sauvegardez à nouveau.

## 📊 Exemple d'utilisation

```python
# Dans le générateur d'invitations
font = self.charger_police(
    font_name="C:/Projets/GestionInvitations/fonts/Elegant.ttf",
    font_size=50
)
```

La méthode `charger_police()` :
1. Essaye de charger la police spécifiée
2. Si échec, essaye les polices système
3. En dernier recours, utilise la police par défaut

## ✅ Vérification

Pour vérifier que vos polices sont bien configurées :

1. Ouvrez l'éditeur de template
2. Chargez votre template
3. Ajoutez un élément de texte
4. Le menu "Police:" doit contenir :
   - "Police par défaut"
   - Vos polices personnalisées du dossier `fonts/`
   - Les polices système détectées

## 🎓 Workflow complet

1. **Téléchargez** une police (.ttf)
2. **Ajoutez-la** via l'éditeur ou copiez-la dans `fonts/`
3. **Ouvrez** l'éditeur de template
4. **Chargez** votre template
5. **Ajoutez** un élément de texte (ex: Nom Complet)
6. **Sélectionnez** votre police dans le menu
7. **Ajustez** la taille et la couleur
8. **Sauvegardez** la configuration
9. **Générez** les invitations

Les invitations utiliseront automatiquement la police que vous avez choisie ! 🎉
