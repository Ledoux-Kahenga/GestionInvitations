"""
Modèle de base de données pour la gestion des invitations
"""
import sqlite3
from datetime import datetime
from config import DATABASE_PATH


class InvitationModel:
    """Gestion de la base de données des invités"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.create_tables()
    
    def connect(self):
        """Établir la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Fermer la connexion"""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def create_tables(self):
        """Créer les tables si elles n'existent pas"""
        self.connect()
        
        # Table des événements
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS evenements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                date TEXT NOT NULL,
                heure TEXT NOT NULL,
                lieu TEXT NOT NULL,
                organisateur TEXT,
                description TEXT,
                template_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des invités
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT,
                telephone TEXT,
                nombre_accompagnants INTEGER DEFAULT 0,
                categorie TEXT,
                qr_code TEXT UNIQUE,
                invitation_path TEXT,
                statut TEXT DEFAULT 'en_attente',
                date_envoi TEXT,
                date_scan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id)
            )
        ''')
        
        # Table des scans (historique)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invite_id INTEGER NOT NULL,
                date_scan TEXT NOT NULL,
                lieu_scan TEXT,
                valide BOOLEAN DEFAULT 1,
                FOREIGN KEY (invite_id) REFERENCES invites(id)
            )
        ''')
        
        self.conn.commit()
        self.disconnect()
    
    # === ÉVÉNEMENTS ===
    
    def ajouter_evenement(self, nom, date, heure, lieu, organisateur="", description="", template_path=""):
        """Ajouter un nouvel événement"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO evenements (nom, date, heure, lieu, organisateur, description, template_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nom, date, heure, lieu, organisateur, description, template_path))
        evenement_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return evenement_id
    
    def obtenir_evenements(self):
        """Obtenir tous les événements"""
        self.connect()
        self.cursor.execute('''
            SELECT id, nom, date, heure, lieu, organisateur, description, template_path, created_at
            FROM evenements
            ORDER BY date DESC
        ''')
        evenements = self.cursor.fetchall()
        self.disconnect()
        return evenements
    
    def obtenir_evenement(self, evenement_id):
        """Obtenir un événement par ID"""
        self.connect()
        self.cursor.execute('''
            SELECT id, nom, date, heure, lieu, organisateur, description, template_path, created_at
            FROM evenements
            WHERE id = ?
        ''', (evenement_id,))
        evenement = self.cursor.fetchone()
        self.disconnect()
        return evenement
    
    # === INVITÉS ===
    
    def ajouter_invite(self, evenement_id, nom, prenom, email="", telephone="", 
                       nombre_accompagnants=0, categorie="Standard", qr_code=None):
        """Ajouter un invité"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO invites (evenement_id, nom, prenom, email, telephone, 
                               nombre_accompagnants, categorie, qr_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (evenement_id, nom, prenom, email, telephone, nombre_accompagnants, categorie, qr_code))
        invite_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return invite_id
    
    def obtenir_invites(self, evenement_id=None):
        """Obtenir tous les invités (optionnellement filtré par événement)"""
        self.connect()
        if evenement_id:
            self.cursor.execute('''
                SELECT id, evenement_id, nom, prenom, email, telephone, 
                       nombre_accompagnants, categorie, qr_code, invitation_path, 
                       statut, date_envoi, date_scan, created_at
                FROM invites
                WHERE evenement_id = ?
                ORDER BY nom, prenom
            ''', (evenement_id,))
        else:
            self.cursor.execute('''
                SELECT id, evenement_id, nom, prenom, email, telephone, 
                       nombre_accompagnants, categorie, qr_code, invitation_path, 
                       statut, date_envoi, date_scan, created_at
                FROM invites
                ORDER BY created_at DESC
            ''')
        invites = self.cursor.fetchall()
        self.disconnect()
        return invites
    
    def obtenir_invite_par_qr(self, qr_code):
        """Obtenir un invité par son QR code"""
        self.connect()
        self.cursor.execute('''
            SELECT id, evenement_id, nom, prenom, email, telephone, 
                   nombre_accompagnants, categorie, qr_code, invitation_path, 
                   statut, date_envoi, date_scan, created_at
            FROM invites
            WHERE qr_code = ?
        ''', (qr_code,))
        invite = self.cursor.fetchone()
        self.disconnect()
        return invite
    
    def mettre_a_jour_invite(self, invite_id, **kwargs):
        """Mettre à jour les informations d'un invité"""
        self.connect()
        
        # Construire la requête dynamiquement
        champs = []
        valeurs = []
        for key, value in kwargs.items():
            champs.append(f"{key} = ?")
            valeurs.append(value)
        
        if champs:
            valeurs.append(invite_id)
            query = f"UPDATE invites SET {', '.join(champs)} WHERE id = ?"
            self.cursor.execute(query, valeurs)
            self.conn.commit()
        
        self.disconnect()
        return True
    
    def supprimer_invite(self, invite_id):
        """Supprimer un invité"""
        self.connect()
        self.cursor.execute("DELETE FROM invites WHERE id = ?", (invite_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    # === SCANS ===
    
    def enregistrer_scan(self, invite_id, lieu_scan="Entrée"):
        """Enregistrer un scan de QR code"""
        self.connect()
        date_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Enregistrer le scan
        self.cursor.execute('''
            INSERT INTO scans (invite_id, date_scan, lieu_scan)
            VALUES (?, ?, ?)
        ''', (invite_id, date_scan, lieu_scan))
        
        # Mettre à jour le statut de l'invité
        self.cursor.execute('''
            UPDATE invites
            SET statut = 'présent', date_scan = ?
            WHERE id = ?
        ''', (date_scan, invite_id))
        
        self.conn.commit()
        self.disconnect()
        return True
    
    def obtenir_scans(self, evenement_id=None):
        """Obtenir l'historique des scans"""
        self.connect()
        if evenement_id:
            self.cursor.execute('''
                SELECT s.id, s.invite_id, s.date_scan, s.lieu_scan, s.valide,
                       i.nom, i.prenom, i.categorie
                FROM scans s
                JOIN invites i ON s.invite_id = i.id
                WHERE i.evenement_id = ?
                ORDER BY s.date_scan DESC
            ''', (evenement_id,))
        else:
            self.cursor.execute('''
                SELECT s.id, s.invite_id, s.date_scan, s.lieu_scan, s.valide,
                       i.nom, i.prenom, i.categorie
                FROM scans s
                JOIN invites i ON s.invite_id = i.id
                ORDER BY s.date_scan DESC
            ''')
        scans = self.cursor.fetchall()
        self.disconnect()
        return scans
    
    # === STATISTIQUES ===
    
    def obtenir_statistiques(self, evenement_id):
        """Obtenir les statistiques d'un événement"""
        self.connect()
        
        # Nombre total d'invités
        self.cursor.execute('''
            SELECT COUNT(*), SUM(nombre_accompagnants + 1)
            FROM invites
            WHERE evenement_id = ?
        ''', (evenement_id,))
        total_invites, total_personnes = self.cursor.fetchone()
        total_personnes = total_personnes or 0
        
        # Invités présents
        self.cursor.execute('''
            SELECT COUNT(*), SUM(nombre_accompagnants + 1)
            FROM invites
            WHERE evenement_id = ? AND statut = 'présent'
        ''', (evenement_id,))
        presents, personnes_presentes = self.cursor.fetchone()
        personnes_presentes = personnes_presentes or 0
        
        # Invités par catégorie
        self.cursor.execute('''
            SELECT categorie, COUNT(*), SUM(nombre_accompagnants + 1),
                   SUM(CASE WHEN statut = 'présent' THEN 1 ELSE 0 END)
            FROM invites
            WHERE evenement_id = ?
            GROUP BY categorie
        ''', (evenement_id,))
        resultats_categories = self.cursor.fetchall()
        
        # Convertir en dictionnaire
        par_categorie = {}
        for row in resultats_categories:
            par_categorie[row[0]] = {
                'nombre': row[1],
                'total_personnes': row[2] or 0,
                'presents': row[3] or 0
            }
        
        self.disconnect()
        
        return {
            'total_invites': total_invites or 0,
            'total_personnes': total_personnes,
            'presents': presents or 0,
            'personnes_presentes': personnes_presentes,
            'taux_presence': round((presents / total_invites * 100) if total_invites > 0 else 0, 2),
            'par_categorie': par_categorie
        }
