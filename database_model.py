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
        
        # Table des tables (placement)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables_event (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                capacite INTEGER DEFAULT 10,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id)
            )
        ''')
        
        # Table des invités
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                titre TEXT DEFAULT '',
                email TEXT,
                telephone TEXT,
                categorie TEXT DEFAULT 'Standard',
                nombre_accompagnants INTEGER DEFAULT 0,
                table_id INTEGER,
                qr_code TEXT UNIQUE,
                invitation_path TEXT,
                statut TEXT DEFAULT 'invité',
                date_envoi TEXT,
                date_scan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                FOREIGN KEY (table_id) REFERENCES tables_event(id)
            )
        ''')
        
        # Migration: ajouter table_id si elle n'existe pas
        try:
            self.cursor.execute("ALTER TABLE invites ADD COLUMN table_id INTEGER")
        except:
            pass  # La colonne existe déjà

        # Migrations: ajouter les champs utilises par l'interface moderne
        try:
            self.cursor.execute("ALTER TABLE invites ADD COLUMN titre TEXT DEFAULT ''")
        except:
            pass  # La colonne existe déjà
        
        try:
            self.cursor.execute("ALTER TABLE invites ADD COLUMN categorie TEXT DEFAULT 'Standard'")
        except:
            pass  # La colonne existe déjà
        
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
    
    def modifier_evenement(self, evenement_id, nom, date, heure, lieu, organisateur="", description="", template_path=""):
        """Modifier un événement existant"""
        self.connect()
        self.cursor.execute('''
            UPDATE evenements 
            SET nom = ?, date = ?, heure = ?, lieu = ?, organisateur = ?, description = ?, template_path = ?
            WHERE id = ?
        ''', (nom, date, heure, lieu, organisateur, description, template_path, evenement_id))
        self.conn.commit()
        self.disconnect()
        return True
    
    def supprimer_evenement(self, evenement_id):
        """Supprimer un événement et tous ses invités"""
        self.connect()
        # Supprimer d'abord les invités associés
        self.cursor.execute("DELETE FROM invites WHERE evenement_id = ?", (evenement_id,))
        # Supprimer les tables associées
        self.cursor.execute("DELETE FROM tables_event WHERE evenement_id = ?", (evenement_id,))
        # Puis supprimer l'événement
        self.cursor.execute("DELETE FROM evenements WHERE id = ?", (evenement_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    # === TABLES (PLACEMENT) ===
    
    def ajouter_table(self, evenement_id, nom, capacite=10, description=""):
        """Ajouter une table à un événement"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO tables_event (evenement_id, nom, capacite, description)
            VALUES (?, ?, ?, ?)
        ''', (evenement_id, nom, capacite, description))
        table_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return table_id
    
    def obtenir_tables(self, evenement_id):
        """Obtenir toutes les tables d'un événement"""
        self.connect()
        self.cursor.execute('''
            SELECT t.id, t.evenement_id, t.nom, t.capacite, t.description, t.created_at,
                   (SELECT COUNT(*) FROM invites WHERE table_id = t.id) as nb_invites,
                   (SELECT SUM(nombre_accompagnants + 1) FROM invites WHERE table_id = t.id) as nb_personnes
            FROM tables_event t
            WHERE t.evenement_id = ?
            ORDER BY t.nom
        ''', (evenement_id,))
        tables = self.cursor.fetchall()
        self.disconnect()
        return tables
    
    def obtenir_table(self, table_id):
        """Obtenir une table par ID"""
        self.connect()
        self.cursor.execute('''
            SELECT id, evenement_id, nom, capacite, description, created_at
            FROM tables_event
            WHERE id = ?
        ''', (table_id,))
        table = self.cursor.fetchone()
        self.disconnect()
        return table
    
    def modifier_table(self, table_id, nom, capacite=10, description=""):
        """Modifier une table"""
        self.connect()
        self.cursor.execute('''
            UPDATE tables_event 
            SET nom = ?, capacite = ?, description = ?
            WHERE id = ?
        ''', (nom, capacite, description, table_id))
        self.conn.commit()
        self.disconnect()
        return True
    
    def supprimer_table(self, table_id):
        """Supprimer une table (les invités sont désassignés)"""
        self.connect()
        # Désassigner les invités de cette table
        self.cursor.execute("UPDATE invites SET table_id = NULL WHERE table_id = ?", (table_id,))
        # Supprimer la table
        self.cursor.execute("DELETE FROM tables_event WHERE id = ?", (table_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    def obtenir_places_disponibles_table(self, table_id, invite_id_exclu=None):
        """Obtenir la capacité restante d'une table."""
        if table_id is None:
            return None
        
        self.connect()
        self.cursor.execute("SELECT nom, capacite FROM tables_event WHERE id = ?", (table_id,))
        table = self.cursor.fetchone()
        
        if not table:
            self.disconnect()
            return None
        
        query = "SELECT COALESCE(SUM(nombre_accompagnants + 1), 0) FROM invites WHERE table_id = ?"
        params = [table_id]
        if invite_id_exclu is not None:
            query += " AND id != ?"
            params.append(invite_id_exclu)
        
        self.cursor.execute(query, params)
        places_occupees = self.cursor.fetchone()[0] or 0
        places_disponibles = table['capacite'] - places_occupees
        self.disconnect()
        
        return {
            'nom': table['nom'],
            'capacite': table['capacite'],
            'occupees': places_occupees,
            'disponibles': max(0, places_disponibles)
        }
    
    def verifier_capacite_table(self, table_id, nombre_personnes, invite_id_exclu=None):
        """Vérifier qu'une table peut accueillir un nombre de personnes."""
        if table_id is None:
            return True, ""
        
        places = self.obtenir_places_disponibles_table(table_id, invite_id_exclu)
        if not places:
            return False, "Table introuvable"
        
        if nombre_personnes > places['disponibles']:
            return False, (
                f"La table '{places['nom']}' n'a plus assez de places "
                f"({places['disponibles']} disponible(s), {nombre_personnes} demandée(s))."
            )
        
        return True, ""
    
    # === INVITÉS ===
    
    def ajouter_invite(self, evenement_id, nom, prenom, email="", telephone="", 
                       nombre_accompagnants=0, table_id=None, qr_code=None,
                       titre="", categorie="Standard"):
        """Ajouter un invité"""
        capacite_ok, message = self.verifier_capacite_table(table_id, nombre_accompagnants + 1)
        if not capacite_ok:
            raise ValueError(message)
        
        self.connect()
        self.cursor.execute('''
            INSERT INTO invites (evenement_id, nom, prenom, titre, email, telephone, 
                               categorie, nombre_accompagnants, table_id, qr_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (evenement_id, nom, prenom, titre, email, telephone, categorie, nombre_accompagnants, table_id, qr_code))
        invite_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return invite_id
    
    def obtenir_invites(self, evenement_id=None):
        """Obtenir tous les invités (optionnellement filtré par événement)"""
        self.connect()
        if evenement_id:
            self.cursor.execute('''
                SELECT i.id, i.evenement_id, i.nom, i.prenom, i.titre, i.email, i.telephone, 
                       i.categorie, i.nombre_accompagnants, i.table_id, t.nom as table_nom, 
                       i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at
                FROM invites i
                LEFT JOIN tables_event t ON i.table_id = t.id
                WHERE i.evenement_id = ?
                ORDER BY i.nom, i.prenom
            ''', (evenement_id,))
        else:
            self.cursor.execute('''
                SELECT i.id, i.evenement_id, i.nom, i.prenom, i.titre, i.email, i.telephone, 
                       i.categorie, i.nombre_accompagnants, i.table_id, t.nom as table_nom, 
                       i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at
                FROM invites i
                LEFT JOIN tables_event t ON i.table_id = t.id
                ORDER BY i.created_at DESC
            ''')
        invites = self.cursor.fetchall()
        self.disconnect()
        return invites
    
    def obtenir_invite_par_qr(self, qr_code):
        """Obtenir un invité par son QR code"""
        self.connect()
        self.cursor.execute('''
            SELECT i.id, i.evenement_id, i.nom, i.prenom, i.titre, i.email, i.telephone, 
                   i.categorie, i.nombre_accompagnants, i.table_id, t.nom as table_nom, 
                   i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at
            FROM invites i
            LEFT JOIN tables_event t ON i.table_id = t.id
            WHERE i.qr_code = ?
        ''', (qr_code,))
        invite = self.cursor.fetchone()
        self.disconnect()
        return invite
    
    def modifier_invite(self, invite_id, nom, prenom, email="", telephone="", 
                        nombre_accompagnants=0, table_id=None, titre="", categorie="Standard"):
        """Modifier un invité"""
        capacite_ok, message = self.verifier_capacite_table(
            table_id, nombre_accompagnants + 1, invite_id_exclu=invite_id
        )
        if not capacite_ok:
            raise ValueError(message)
        
        self.connect()
        self.cursor.execute('''
            UPDATE invites 
            SET nom = ?, prenom = ?, titre = ?, email = ?, telephone = ?, categorie = ?, nombre_accompagnants = ?, table_id = ?
            WHERE id = ?
        ''', (nom, prenom, titre, email, telephone, categorie, nombre_accompagnants, table_id, invite_id))
        self.conn.commit()
        self.disconnect()
        return True
    
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
        
        # Invités par table
        self.cursor.execute('''
            SELECT COALESCE(t.nom, 'Non assigné'), COUNT(*), SUM(i.nombre_accompagnants + 1),
                   SUM(CASE WHEN i.statut = 'présent' THEN 1 ELSE 0 END)
            FROM invites i
            LEFT JOIN tables_event t ON i.table_id = t.id
            WHERE i.evenement_id = ?
            GROUP BY i.table_id
        ''', (evenement_id,))
        resultats_tables = self.cursor.fetchall()
        
        # Convertir en dictionnaire
        par_table = {}
        for row in resultats_tables:
            par_table[row[0]] = {
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
            'par_table': par_table
        }
