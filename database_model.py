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
        
        # Table des tables (placement) - DOIT être créée avant invites pour foreign key
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                nom_table TEXT NOT NULL,
                cote TEXT NOT NULL,
                capacite INTEGER DEFAULT 10,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id)
            )
        ''')
        
        # Vérifier si la table invites existe déjà
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invites'")
        table_exists = self.cursor.fetchone()
        
        if table_exists:
            # Vérifier si les anciennes colonnes existent
            self.cursor.execute("PRAGMA table_info(invites)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'nom' in columns and 'prenom' in columns:
                # Migration nécessaire: ancien schéma détecté
                print("Migration de la base de données détectée...")
                
                # Créer une table temporaire avec le nouveau schéma
                self.cursor.execute('''
                    CREATE TABLE invites_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        evenement_id INTEGER NOT NULL,
                        civilite TEXT NOT NULL DEFAULT 'Mr',
                        nom_complet TEXT NOT NULL,
                        table_id INTEGER,
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
                        FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                        FOREIGN KEY (table_id) REFERENCES tables(id)
                    )
                ''')
                
                # Copier les données avec transformation
                self.cursor.execute('''
                    INSERT INTO invites_new (
                        id, evenement_id, civilite, nom_complet, table_id, 
                        email, telephone, nombre_accompagnants, categorie, 
                        qr_code, invitation_path, statut, date_envoi, date_scan, created_at
                    )
                    SELECT 
                        id, evenement_id, 'Mr', 
                        CASE 
                            WHEN prenom IS NOT NULL AND prenom != '' 
                            THEN prenom || ' ' || nom 
                            ELSE nom 
                        END as nom_complet,
                        NULL,
                        email, telephone, nombre_accompagnants, categorie, 
                        qr_code, invitation_path, statut, date_envoi, date_scan, created_at
                    FROM invites
                ''')
                
                # Supprimer l'ancienne table et renommer la nouvelle
                self.cursor.execute("DROP TABLE invites")
                self.cursor.execute("ALTER TABLE invites_new RENAME TO invites")
                print("Migration terminée avec succès!")
            elif 'civilite' in columns and 'table_id' not in columns:
                # Colonne civilite existe mais pas table_id: migration partielle nécessaire
                print("Ajout de la colonne table_id...")
                self.cursor.execute("ALTER TABLE invites ADD COLUMN table_id INTEGER REFERENCES tables(id)")
                # Supprimer la colonne nom_table si elle existe
                self.cursor.execute("PRAGMA table_info(invites)")
                columns = [col[1] for col in self.cursor.fetchall()]
                if 'nom_table' in columns:
                    # SQLite ne supporte pas DROP COLUMN avant version 3.35.0
                    # On va créer une nouvelle table sans nom_table
                    self.cursor.execute('''
                        CREATE TABLE invites_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            evenement_id INTEGER NOT NULL,
                            civilite TEXT NOT NULL DEFAULT 'Mr',
                            nom_complet TEXT NOT NULL,
                            table_id INTEGER,
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
                            FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                            FOREIGN KEY (table_id) REFERENCES tables(id)
                        )
                    ''')
                    self.cursor.execute('''
                        INSERT INTO invites_new 
                        SELECT id, evenement_id, civilite, nom_complet, NULL, 
                               email, telephone, nombre_accompagnants, categorie, 
                               qr_code, invitation_path, statut, date_envoi, date_scan, created_at
                        FROM invites
                    ''')
                    self.cursor.execute("DROP TABLE invites")
                    self.cursor.execute("ALTER TABLE invites_new RENAME TO invites")
                print("Colonne table_id ajoutée!")
        else:
            # Table invites n'existe pas: création avec le nouveau schéma
            self.cursor.execute('''
                CREATE TABLE invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evenement_id INTEGER NOT NULL,
                    civilite TEXT NOT NULL DEFAULT 'Mr',
                    nom_complet TEXT NOT NULL,
                    table_id INTEGER,
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
                    FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                    FOREIGN KEY (table_id) REFERENCES tables(id)
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
        self.cursor.execute("DELETE FROM tables WHERE evenement_id = ?", (evenement_id,))
        # Puis supprimer l'événement
        self.cursor.execute("DELETE FROM evenements WHERE id = ?", (evenement_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    # === TABLES ===
    
    def ajouter_table(self, evenement_id, nom_table, cote, capacite=10, description=""):
        """Ajouter une nouvelle table"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO tables (evenement_id, nom_table, cote, capacite, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (evenement_id, nom_table, cote, capacite, description))
        table_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return table_id
    
    def obtenir_tables(self, evenement_id):
        """Obtenir toutes les tables d'un événement"""
        self.connect()
        self.cursor.execute('''
            SELECT id, evenement_id, nom_table, cote, capacite, description, created_at
            FROM tables
            WHERE evenement_id = ?
            ORDER BY cote, nom_table
        ''', (evenement_id,))
        tables = self.cursor.fetchall()
        self.disconnect()
        return tables
    
    def obtenir_table(self, table_id):
        """Obtenir une table par ID"""
        self.connect()
        self.cursor.execute('''
            SELECT id, evenement_id, nom_table, cote, capacite, description, created_at
            FROM tables
            WHERE id = ?
        ''', (table_id,))
        table = self.cursor.fetchone()
        self.disconnect()
        return table
    
    def modifier_table(self, table_id, nom_table, cote, capacite=10, description=""):
        """Modifier une table existante"""
        self.connect()
        self.cursor.execute('''
            UPDATE tables 
            SET nom_table = ?, cote = ?, capacite = ?, description = ?
            WHERE id = ?
        ''', (nom_table, cote, capacite, description, table_id))
        self.conn.commit()
        self.disconnect()
        return True
    
    def supprimer_table(self, table_id):
        """Supprimer une table (met à NULL les invités associés)"""
        self.connect()
        # Mettre à NULL les invités qui référencent cette table
        self.cursor.execute("UPDATE invites SET table_id = NULL WHERE table_id = ?", (table_id,))
        # Supprimer la table
        self.cursor.execute("DELETE FROM tables WHERE id = ?", (table_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    def verifier_capacite_table(self, table_id):
        """Vérifier si une table a encore de la place disponible
        Retourne (places_occupees, capacite_totale, places_disponibles)"""
        self.connect()
        
        # Obtenir la capacité de la table
        self.cursor.execute('''
            SELECT capacite FROM tables WHERE id = ?
        ''', (table_id,))
        result = self.cursor.fetchone()
        
        if not result:
            self.disconnect()
            return None
        
        capacite_totale = result['capacite']
        
        # Compter le nombre de places occupées (invité + accompagnants)
        self.cursor.execute('''
            SELECT SUM(1 + nombre_accompagnants) as places_occupees
            FROM invites
            WHERE table_id = ?
        ''', (table_id,))
        result = self.cursor.fetchone()
        places_occupees = result['places_occupees'] or 0
        
        self.disconnect()
        
        places_disponibles = capacite_totale - places_occupees
        return (places_occupees, capacite_totale, places_disponibles)
    
    def obtenir_tables_avec_places(self, evenement_id):
        """Obtenir toutes les tables avec le nombre de places occupées et disponibles"""
        self.connect()
        self.cursor.execute('''
            SELECT 
                t.id, 
                t.evenement_id, 
                t.nom_table, 
                t.cote, 
                t.capacite, 
                t.description, 
                t.created_at,
                COALESCE(SUM(1 + i.nombre_accompagnants), 0) as places_occupees
            FROM tables t
            LEFT JOIN invites i ON t.id = i.table_id
            WHERE t.evenement_id = ?
            GROUP BY t.id, t.nom_table, t.cote, t.capacite, t.description, t.created_at
            ORDER BY t.cote, t.nom_table
        ''', (evenement_id,))
        tables = self.cursor.fetchall()
        self.disconnect()
        return tables
    
    # === INVITÉS ===
    
    def ajouter_invite(self, evenement_id, civilite, nom_complet, table_id=None, email="", telephone="", 
                      nombre_accompagnants=0, categorie="Standard", qr_code=""):
        """Ajouter un nouvel invité"""
        import uuid
        
        # Générer un QR code unique si non fourni
        if not qr_code:
            qr_code = f"INVITE-TEMP-{uuid.uuid4().hex[:12]}"
        
        self.connect()
        self.cursor.execute('''
            INSERT INTO invites (evenement_id, civilite, nom_complet, table_id, email, telephone, 
                               nombre_accompagnants, categorie, qr_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (evenement_id, civilite, nom_complet, table_id, email, telephone, nombre_accompagnants, categorie, qr_code))
        invite_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return invite_id
    
    def obtenir_invites(self, evenement_id=None):
        """Obtenir tous les invités (optionnellement filtré par événement)"""
        self.connect()
        if evenement_id:
            self.cursor.execute('''
                SELECT i.id, i.evenement_id, i.civilite, i.nom_complet, t.nom_table, 
                       i.email, i.telephone, i.nombre_accompagnants, i.categorie, 
                       i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at
                FROM invites i
                LEFT JOIN tables t ON i.table_id = t.id
                WHERE i.evenement_id = ?
                ORDER BY i.nom_complet
            ''', (evenement_id,))
        else:
            self.cursor.execute('''
                SELECT i.id, i.evenement_id, i.civilite, i.nom_complet, t.nom_table, 
                       i.email, i.telephone, i.nombre_accompagnants, i.categorie, 
                       i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at
                FROM invites i
                LEFT JOIN tables t ON i.table_id = t.id
                ORDER BY i.created_at DESC
            ''')
        invites = self.cursor.fetchall()
        self.disconnect()
        return invites
    
    def obtenir_invite_par_qr(self, qr_code):
        """Obtenir un invité par son QR code avec infos événement et table"""
        self.connect()
        self.cursor.execute('''
            SELECT i.id, i.evenement_id, i.civilite, i.nom_complet, t.nom_table, 
                   i.email, i.telephone, i.nombre_accompagnants, i.categorie, 
                   i.qr_code, i.invitation_path, i.statut, i.date_envoi, i.date_scan, i.created_at,
                   e.nom as nom_evenement, e.date as date_evenement, e.heure as heure_evenement
            FROM invites i
            LEFT JOIN tables t ON i.table_id = t.id
            LEFT JOIN evenements e ON i.evenement_id = e.id
            WHERE i.qr_code = ?
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
