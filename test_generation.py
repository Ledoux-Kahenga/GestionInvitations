"""
Script de test - Génération d'invitations
"""
from database_model import InvitationModel
from invitation_generator import InvitationGenerator
from datetime import datetime

# Initialiser la base de données
db = InvitationModel()
db.create_tables()

# Créer un événement de test
print("📅 Création de l'événement de test...")
event_id = db.ajouter_evenement(
    nom="Gala de Charité 2025",
    date="2025-12-31",
    heure="19:00",
    lieu="Grand Hôtel Paris",
    organisateur="Association Solidarité",
    description="Soirée de gala pour lever des fonds"
)
print(f"✅ Événement créé avec ID: {event_id}")

# Ajouter quelques invités de test
print("\n👥 Ajout des invités de test...")
invites_test = [
    {
        'nom': 'Dupont',
        'prenom': 'Jean',
        'email': 'jean.dupont@example.com',
        'telephone': '0601020304',
        'categorie': 'VIP',
        'accompagnants': 1
    },
    {
        'nom': 'Martin',
        'prenom': 'Marie',
        'email': 'marie.martin@example.com',
        'telephone': '0605060708',
        'categorie': 'Standard',
        'accompagnants': 0
    },
    {
        'nom': 'Bernard',
        'prenom': 'Paul',
        'email': 'paul.bernard@example.com',
        'telephone': '0609101112',
        'categorie': 'Presse',
        'accompagnants': 0
    },
    {
        'nom': 'Durand',
        'prenom': 'Sophie',
        'email': 'sophie.durand@example.com',
        'telephone': '0613141516',
        'categorie': 'VIP',
        'accompagnants': 2
    },
    {
        'nom': 'Petit',
        'prenom': 'Luc',
        'email': 'luc.petit@example.com',
        'telephone': '0617181920',
        'categorie': 'Invité spécial',
        'accompagnants': 1
    }
]

invite_ids = []
for inv in invites_test:
    invite_id = db.ajouter_invite(
        event_id,
        inv['nom'],
        inv['prenom'],
        inv['email'],
        inv['telephone'],
        inv['accompagnants'],
        inv['categorie']
    )
    invite_ids.append(invite_id)
    print(f"  ✓ {inv['prenom']} {inv['nom']} ({inv['categorie']}) - ID: {invite_id}")

print(f"\n✅ {len(invite_ids)} invités ajoutés")

# Récupérer l'événement et les invités
print("\n🎨 Génération des invitations...")
event = db.obtenir_evenement(event_id)
invites = db.obtenir_invites(event_id)

# Initialiser le générateur
generator = InvitationGenerator()

# Générer chaque invitation
for invite in invites:
    invite_data = {
        'id': invite['id'],
        'nom': invite['nom'],
        'prenom': invite['prenom'],
        'categorie': invite['categorie'],
        'evenement': {
            'nom': event['nom'],
            'date': event['date'],
            'heure': event['heure'],
            'lieu': event['lieu']
        }
    }
    
    try:
        path, qr_code = generator.creer_invitation(invite_data)
        
        # Mettre à jour la base de données
        db.mettre_a_jour_invite(
            invite['id'],
            qr_code=qr_code,
            invitation_path=path
        )
        
        print(f"  ✓ {invite['prenom']} {invite['nom']}")
        print(f"    📄 Invitation: {path}")
        print(f"    📱 QR Code: {qr_code}")
        
    except Exception as e:
        print(f"  ❌ Erreur pour {invite['prenom']} {invite['nom']}: {e}")

# Afficher les statistiques
print("\n📊 Statistiques de l'événement:")
stats = db.obtenir_statistiques(event_id)
print(f"  Total invités: {stats['total_invites']}")
print(f"  Total personnes (avec accompagnants): {stats['total_personnes']}")
print(f"  Présents: {stats['presents']}")
print(f"  Taux de présence: {stats['taux_presence']:.1f}%")

print("\n📊 Répartition par catégorie:")
for cat, data in stats['par_categorie'].items():
    print(f"  {cat}: {data['nombre']} invités, {data['total_personnes']} personnes")

# Test de scan simulé
print("\n📱 Simulation de scans...")
# Simuler quelques arrivées
invites_a_scanner = invites[:3]  # Les 3 premiers

for invite in invites_a_scanner:
    success = db.enregistrer_scan(invite['id'], "Entrée principale")
    if success:
        print(f"  ✓ Scan validé: {invite['prenom']} {invite['nom']}")

# Afficher les stats mises à jour
print("\n📊 Statistiques après scans:")
stats = db.obtenir_statistiques(event_id)
print(f"  Présents: {stats['presents']}/{stats['total_invites']}")
print(f"  Personnes présentes: {stats['personnes_presentes']}/{stats['total_personnes']}")
print(f"  Taux de présence: {stats['taux_presence']:.1f}%")

print("\n✨ Test terminé avec succès!")
print(f"\nVous pouvez maintenant:")
print(f"  1. Consulter les invitations dans: invitations_generees/")
print(f"  2. Consulter les QR codes dans: qrcodes/")
print(f"  3. Lancer l'application GUI: python main.py")
