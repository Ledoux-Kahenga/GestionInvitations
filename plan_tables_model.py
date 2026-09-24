"""
Modèle de base de données pour la gestion du plan de tables (mariages)
"""
import sqlite3
from datetime import datetime
from config import DATABASE_PATH


class PlanTablesModel:
    """Gestion de la base de données du plan de tables pour mariages"""
    
    # Tags de relation disponibles
    RELATION_TAGS = ["Famille", "Amis", "Collègues", "Voisins", "VIP"]
    
    # Types d'unités d'invitation
    UNIT_TYPES = ["individu", "couple", "groupe"]
    
    # Catégories (côtés)
    CATEGORIES = ["Mari", "Mariée"]
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.create_tables()
    
    def connect(self):
        """Établir la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Fermer la connexion"""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def create_tables(self):
        """Créer les tables si elles n'existent pas"""
        self.connect()
        
        # Table des tables de mariage (avec catégorie Mari/Mariée)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables_mariage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                numero INTEGER NOT NULL,
                nom TEXT NOT NULL,
                categorie TEXT NOT NULL CHECK(categorie IN ('Mari', 'Mariée')),
                capacite_max INTEGER NOT NULL DEFAULT 10,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                UNIQUE(evenement_id, numero)
            )
        ''')
        
        # Table des unités d'invitation (individus, couples, groupes)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS unites_invitation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evenement_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                type_unite TEXT NOT NULL CHECK(type_unite IN ('individu', 'couple', 'groupe')),
                taille INTEGER NOT NULL DEFAULT 1,
                categorie TEXT NOT NULL CHECK(categorie IN ('Mari', 'Mariée')),
                relation_tag TEXT NOT NULL CHECK(relation_tag IN ('Famille', 'Amis', 'Collègues', 'Voisins', 'VIP')),
                table_id INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evenement_id) REFERENCES evenements(id),
                FOREIGN KEY (table_id) REFERENCES tables_mariage(id)
            )
        ''')
        
        # Table des membres d'une unité (pour stocker les noms individuels)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS membres_unite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unite_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (unite_id) REFERENCES unites_invitation(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        self.disconnect()
    
    # === TABLES DE MARIAGE ===
    
    def ajouter_table_mariage(self, evenement_id, numero, nom, categorie, capacite_max=10, description=""):
        """Ajouter une table de mariage"""
        if categorie not in self.CATEGORIES:
            raise ValueError(f"Catégorie invalide. Choix: {self.CATEGORIES}")
        
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO tables_mariage (evenement_id, numero, nom, categorie, capacite_max, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (evenement_id, numero, nom, categorie, capacite_max, description))
            table_id = self.cursor.lastrowid
            self.conn.commit()
            return table_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Le numéro de table {numero} existe déjà pour cet événement")
            raise
        finally:
            self.disconnect()
    
    def obtenir_tables_mariage(self, evenement_id):
        """Obtenir toutes les tables d'un événement avec leurs statistiques"""
        self.connect()
        self.cursor.execute('''
            SELECT 
                t.id, t.evenement_id, t.numero, t.nom, t.categorie, 
                t.capacite_max, t.description, t.created_at,
                COALESCE(SUM(u.taille), 0) as places_occupees,
                t.capacite_max - COALESCE(SUM(u.taille), 0) as places_libres,
                COUNT(u.id) as nb_unites,
                GROUP_CONCAT(DISTINCT u.relation_tag) as tags_presents
            FROM tables_mariage t
            LEFT JOIN unites_invitation u ON u.table_id = t.id
            WHERE t.evenement_id = ?
            GROUP BY t.id
            ORDER BY t.categorie, t.numero
        ''', (evenement_id,))
        tables = self.cursor.fetchall()
        self.disconnect()
        return tables
    
    def obtenir_table_mariage(self, table_id):
        """Obtenir une table par ID avec ses statistiques"""
        self.connect()
        self.cursor.execute('''
            SELECT 
                t.id, t.evenement_id, t.numero, t.nom, t.categorie, 
                t.capacite_max, t.description, t.created_at,
                COALESCE(SUM(u.taille), 0) as places_occupees,
                t.capacite_max - COALESCE(SUM(u.taille), 0) as places_libres
            FROM tables_mariage t
            LEFT JOIN unites_invitation u ON u.table_id = t.id
            WHERE t.id = ?
            GROUP BY t.id
        ''', (table_id,))
        table = self.cursor.fetchone()
        self.disconnect()
        return table
    
    def modifier_table_mariage(self, table_id, numero=None, nom=None, categorie=None, 
                                capacite_max=None, description=None):
        """Modifier une table existante"""
        self.connect()
        
        # Construire la requête dynamiquement
        updates = []
        valeurs = []
        
        if numero is not None:
            updates.append("numero = ?")
            valeurs.append(numero)
        if nom is not None:
            updates.append("nom = ?")
            valeurs.append(nom)
        if categorie is not None:
            if categorie not in self.CATEGORIES:
                self.disconnect()
                raise ValueError(f"Catégorie invalide. Choix: {self.CATEGORIES}")
            updates.append("categorie = ?")
            valeurs.append(categorie)
        if capacite_max is not None:
            # Vérifier que la nouvelle capacité est suffisante
            self.cursor.execute('''
                SELECT COALESCE(SUM(taille), 0) FROM unites_invitation WHERE table_id = ?
            ''', (table_id,))
            places_occupees = self.cursor.fetchone()[0]
            if capacite_max < places_occupees:
                self.disconnect()
                raise ValueError(f"Capacité insuffisante: {places_occupees} places déjà occupées")
            updates.append("capacite_max = ?")
            valeurs.append(capacite_max)
        if description is not None:
            updates.append("description = ?")
            valeurs.append(description)
        
        if updates:
            valeurs.append(table_id)
            query = f"UPDATE tables_mariage SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, valeurs)
            self.conn.commit()
        
        self.disconnect()
        return True
    
    def supprimer_table_mariage(self, table_id):
        """Supprimer une table (les unités sont désassignées)"""
        self.connect()
        # Désassigner les unités de cette table
        self.cursor.execute("UPDATE unites_invitation SET table_id = NULL WHERE table_id = ?", (table_id,))
        # Supprimer la table
        self.cursor.execute("DELETE FROM tables_mariage WHERE id = ?", (table_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    def compter_tables_mariage(self, evenement_id):
        """Compter le nombre de tables pour un événement"""
        self.connect()
        self.cursor.execute('''
            SELECT COUNT(*) FROM tables_mariage WHERE evenement_id = ?
        ''', (evenement_id,))
        count = self.cursor.fetchone()[0]
        self.disconnect()
        return count
    
    # === UNITÉS D'INVITATION ===
    
    def ajouter_unite_invitation(self, evenement_id, nom, type_unite, categorie, 
                                  relation_tag, taille=1, notes="", membres=None):
        """
        Ajouter une unité d'invitation
        
        Args:
            evenement_id: ID de l'événement
            nom: Nom de l'unité (ex: "Famille Dupont", "Mr Smith")
            type_unite: 'individu', 'couple', ou 'groupe'
            categorie: 'Mari' ou 'Mariée'
            relation_tag: 'Famille', 'Amis', 'Collègues', 'Voisins', 'VIP'
            taille: Nombre de personnes (1 pour individu, 2 pour couple, N pour groupe)
            notes: Notes optionnelles
            membres: Liste de dictionnaires {'nom': ..., 'prenom': ...} pour les membres
        """
        if type_unite not in self.UNIT_TYPES:
            raise ValueError(f"Type d'unité invalide. Choix: {self.UNIT_TYPES}")
        if categorie not in self.CATEGORIES:
            raise ValueError(f"Catégorie invalide. Choix: {self.CATEGORIES}")
        if relation_tag not in self.RELATION_TAGS:
            raise ValueError(f"Tag de relation invalide. Choix: {self.RELATION_TAGS}")
        
        # Valider la taille selon le type
        if type_unite == 'individu':
            taille = 1
        elif type_unite == 'couple':
            taille = 2
        elif type_unite == 'groupe' and taille < 2:
            raise ValueError("Un groupe doit avoir au moins 2 personnes")
        
        self.connect()
        self.cursor.execute('''
            INSERT INTO unites_invitation (evenement_id, nom, type_unite, taille, categorie, relation_tag, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (evenement_id, nom, type_unite, taille, categorie, relation_tag, notes))
        unite_id = self.cursor.lastrowid
        
        # Ajouter les membres si fournis
        if membres:
            for membre in membres:
                self.cursor.execute('''
                    INSERT INTO membres_unite (unite_id, nom, prenom)
                    VALUES (?, ?, ?)
                ''', (unite_id, membre.get('nom', ''), membre.get('prenom', '')))
        
        self.conn.commit()
        self.disconnect()
        return unite_id
    
    def obtenir_unites_invitation(self, evenement_id, categorie=None, table_id=None, 
                                   non_placees_seulement=False):
        """
        Obtenir les unités d'invitation avec filtres optionnels
        
        Args:
            evenement_id: ID de l'événement
            categorie: Filtrer par catégorie ('Mari' ou 'Mariée')
            table_id: Filtrer par table assignée
            non_placees_seulement: Si True, retourne uniquement les unités non assignées
        """
        self.connect()
        
        query = '''
            SELECT 
                u.id, u.evenement_id, u.nom, u.type_unite, u.taille,
                u.categorie, u.relation_tag, u.table_id, u.notes, u.created_at,
                t.nom as table_nom, t.numero as table_numero
            FROM unites_invitation u
            LEFT JOIN tables_mariage t ON u.table_id = t.id
            WHERE u.evenement_id = ?
        '''
        params = [evenement_id]
        
        if categorie:
            query += " AND u.categorie = ?"
            params.append(categorie)
        
        if table_id:
            query += " AND u.table_id = ?"
            params.append(table_id)
        elif non_placees_seulement:
            query += " AND u.table_id IS NULL"
        
        query += " ORDER BY u.taille DESC, u.nom"
        
        self.cursor.execute(query, params)
        unites = self.cursor.fetchall()
        self.disconnect()
        return unites
    
    def obtenir_unite_invitation(self, unite_id):
        """Obtenir une unité par ID avec ses membres"""
        self.connect()
        self.cursor.execute('''
            SELECT 
                u.id, u.evenement_id, u.nom, u.type_unite, u.taille,
                u.categorie, u.relation_tag, u.table_id, u.notes, u.created_at,
                t.nom as table_nom, t.numero as table_numero
            FROM unites_invitation u
            LEFT JOIN tables_mariage t ON u.table_id = t.id
            WHERE u.id = ?
        ''', (unite_id,))
        unite = self.cursor.fetchone()
        
        if unite:
            # Récupérer les membres
            self.cursor.execute('''
                SELECT id, nom, prenom FROM membres_unite WHERE unite_id = ?
            ''', (unite_id,))
            membres = self.cursor.fetchall()
            self.disconnect()
            return dict(unite), [dict(m) for m in membres]
        
        self.disconnect()
        return None, []
    
    def modifier_unite_invitation(self, unite_id, nom=None, type_unite=None, taille=None,
                                   categorie=None, relation_tag=None, notes=None):
        """Modifier une unité d'invitation"""
        self.connect()
        
        updates = []
        valeurs = []
        
        if nom is not None:
            updates.append("nom = ?")
            valeurs.append(nom)
        if type_unite is not None:
            if type_unite not in self.UNIT_TYPES:
                self.disconnect()
                raise ValueError(f"Type d'unité invalide. Choix: {self.UNIT_TYPES}")
            updates.append("type_unite = ?")
            valeurs.append(type_unite)
        if taille is not None:
            updates.append("taille = ?")
            valeurs.append(taille)
        if categorie is not None:
            if categorie not in self.CATEGORIES:
                self.disconnect()
                raise ValueError(f"Catégorie invalide. Choix: {self.CATEGORIES}")
            updates.append("categorie = ?")
            valeurs.append(categorie)
        if relation_tag is not None:
            if relation_tag not in self.RELATION_TAGS:
                self.disconnect()
                raise ValueError(f"Tag invalide. Choix: {self.RELATION_TAGS}")
            updates.append("relation_tag = ?")
            valeurs.append(relation_tag)
        if notes is not None:
            updates.append("notes = ?")
            valeurs.append(notes)
        
        if updates:
            valeurs.append(unite_id)
            query = f"UPDATE unites_invitation SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, valeurs)
            self.conn.commit()
        
        self.disconnect()
        return True
    
    def supprimer_unite_invitation(self, unite_id):
        """Supprimer une unité d'invitation et ses membres"""
        self.connect()
        # Supprimer les membres
        self.cursor.execute("DELETE FROM membres_unite WHERE unite_id = ?", (unite_id,))
        # Supprimer l'unité
        self.cursor.execute("DELETE FROM unites_invitation WHERE id = ?", (unite_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    # === AFFECTATION AUX TABLES ===
    
    def assigner_unite_a_table(self, unite_id, table_id):
        """
        Assigner une unité à une table avec validation des contraintes
        
        Returns:
            (success: bool, message: str)
        """
        self.connect()
        
        # Récupérer l'unité
        self.cursor.execute('''
            SELECT id, nom, taille, categorie, relation_tag 
            FROM unites_invitation WHERE id = ?
        ''', (unite_id,))
        unite = self.cursor.fetchone()
        
        if not unite:
            self.disconnect()
            return False, "Unité non trouvée"
        
        # Récupérer la table avec ses statistiques
        self.cursor.execute('''
            SELECT 
                t.id, t.nom, t.categorie, t.capacite_max,
                COALESCE(SUM(u.taille), 0) as places_occupees
            FROM tables_mariage t
            LEFT JOIN unites_invitation u ON u.table_id = t.id
            WHERE t.id = ?
            GROUP BY t.id
        ''', (table_id,))
        table = self.cursor.fetchone()
        
        if not table:
            self.disconnect()
            return False, "Table non trouvée"
        
        # Contrainte 1: Vérifier la catégorie (Mari/Mariée)
        if unite['categorie'] != table['categorie']:
            self.disconnect()
            return False, f"L'unité '{unite['nom']}' ({unite['categorie']}) ne peut pas être placée sur la table '{table['nom']}' ({table['categorie']})"
        
        # Contrainte 2: Vérifier la capacité
        places_libres = table['capacite_max'] - table['places_occupees']
        if unite['taille'] > places_libres:
            self.disconnect()
            return False, f"Capacité insuffisante: l'unité '{unite['nom']}' nécessite {unite['taille']} places, mais seulement {places_libres} disponibles sur '{table['nom']}'"
        
        # Assigner
        self.cursor.execute('''
            UPDATE unites_invitation SET table_id = ? WHERE id = ?
        ''', (table_id, unite_id))
        self.conn.commit()
        self.disconnect()
        
        return True, f"Unité '{unite['nom']}' assignée à la table '{table['nom']}'"
    
    def desassigner_unite(self, unite_id):
        """Retirer une unité de sa table"""
        self.connect()
        self.cursor.execute('''
            UPDATE unites_invitation SET table_id = NULL WHERE id = ?
        ''', (unite_id,))
        self.conn.commit()
        self.disconnect()
        return True
    
    # === ALGORITHME D'AFFECTATION AUTOMATIQUE ===
    
    def auto_assigner_unites(self, evenement_id, respect_affinites=True):
        """
        Algorithme d'affectation automatique des unités aux tables
        
        Logique:
        1. Filtrage par catégorie (Mari vs Mariée)
        2. Tri par taille décroissante (Groupes > Couples > Individus)
        3. Placement avec priorité aux affinités (même tag)
        
        Args:
            evenement_id: ID de l'événement
            respect_affinites: Si True, privilégie les tables avec le même tag
        
        Returns:
            dict avec résultats: {
                'success': int,
                'failed': list[dict],
                'details': list[str]
            }
        """
        self.connect()
        
        results = {
            'success': 0,
            'failed': [],
            'details': []
        }
        
        # Récupérer toutes les unités non placées, triées par taille décroissante
        self.cursor.execute('''
            SELECT id, nom, taille, categorie, relation_tag
            FROM unites_invitation
            WHERE evenement_id = ? AND table_id IS NULL
            ORDER BY taille DESC, nom
        ''', (evenement_id,))
        unites = self.cursor.fetchall()
        
        for unite in unites:
            # Chercher une table compatible
            self.cursor.execute('''
                SELECT 
                    t.id, t.nom, t.capacite_max,
                    COALESCE(SUM(u.taille), 0) as places_occupees,
                    t.capacite_max - COALESCE(SUM(u.taille), 0) as places_libres,
                    GROUP_CONCAT(DISTINCT u.relation_tag) as tags_presents
                FROM tables_mariage t
                LEFT JOIN unites_invitation u ON u.table_id = t.id
                WHERE t.evenement_id = ? AND t.categorie = ?
                GROUP BY t.id
                HAVING places_libres >= ?
                ORDER BY 
                    CASE WHEN tags_presents LIKE ? THEN 0 ELSE 1 END,
                    places_libres ASC
            ''', (evenement_id, unite['categorie'], unite['taille'], 
                  f"%{unite['relation_tag']}%"))
            
            table = self.cursor.fetchone()
            
            if table:
                # Assigner l'unité à la table
                self.cursor.execute('''
                    UPDATE unites_invitation SET table_id = ? WHERE id = ?
                ''', (table['id'], unite['id']))
                results['success'] += 1
                results['details'].append(
                    f"✅ '{unite['nom']}' ({unite['taille']} pers.) → Table '{table['nom']}'"
                )
            else:
                # Échec du placement
                results['failed'].append({
                    'id': unite['id'],
                    'nom': unite['nom'],
                    'taille': unite['taille'],
                    'categorie': unite['categorie'],
                    'tag': unite['relation_tag']
                })
                results['details'].append(
                    f"❌ Impossible de placer '{unite['nom']}' ({unite['taille']} pers., {unite['categorie']})"
                )
        
        self.conn.commit()
        self.disconnect()
        
        return results
    
    # === STATISTIQUES ===
    
    def obtenir_statistiques_plan(self, evenement_id):
        """Obtenir les statistiques du plan de tables"""
        self.connect()
        
        stats = {}
        
        # Statistiques globales
        self.cursor.execute('''
            SELECT 
                COUNT(*) as nb_tables,
                SUM(capacite_max) as capacite_totale
            FROM tables_mariage
            WHERE evenement_id = ?
        ''', (evenement_id,))
        row = self.cursor.fetchone()
        stats['nb_tables'] = row['nb_tables'] or 0
        stats['capacite_totale'] = row['capacite_totale'] or 0
        
        # Statistiques par catégorie
        self.cursor.execute('''
            SELECT 
                categorie,
                COUNT(*) as nb_tables,
                SUM(capacite_max) as capacite
            FROM tables_mariage
            WHERE evenement_id = ?
            GROUP BY categorie
        ''', (evenement_id,))
        stats['par_categorie'] = {row['categorie']: dict(row) for row in self.cursor.fetchall()}
        
        # Statistiques des unités
        self.cursor.execute('''
            SELECT 
                COUNT(*) as nb_unites,
                SUM(taille) as nb_personnes,
                SUM(CASE WHEN table_id IS NOT NULL THEN 1 ELSE 0 END) as nb_placees,
                SUM(CASE WHEN table_id IS NOT NULL THEN taille ELSE 0 END) as personnes_placees
            FROM unites_invitation
            WHERE evenement_id = ?
        ''', (evenement_id,))
        row = self.cursor.fetchone()
        stats['nb_unites'] = row['nb_unites'] or 0
        stats['nb_personnes'] = row['nb_personnes'] or 0
        stats['nb_placees'] = row['nb_placees'] or 0
        stats['personnes_placees'] = row['personnes_placees'] or 0
        stats['nb_non_placees'] = stats['nb_unites'] - stats['nb_placees']
        
        # Statistiques par tag
        self.cursor.execute('''
            SELECT 
                relation_tag,
                COUNT(*) as nb_unites,
                SUM(taille) as nb_personnes
            FROM unites_invitation
            WHERE evenement_id = ?
            GROUP BY relation_tag
        ''', (evenement_id,))
        stats['par_tag'] = {row['relation_tag']: dict(row) for row in self.cursor.fetchall()}
        
        self.disconnect()
        return stats
    
    def exporter_json(self, evenement_id):
        """Exporter le plan de tables en JSON (format demandé dans le cahier des charges)"""
        import json
        
        tables = self.obtenir_tables_mariage(evenement_id)
        unites = self.obtenir_unites_invitation(evenement_id)
        
        data = {
            "tables": [
                {
                    "id": t['id'],
                    "numero": t['numero'],
                    "name": t['nom'],
                    "capacity": t['capacite_max'],
                    "side": t['categorie'],
                    "tags": t['tags_presents'].split(',') if t['tags_presents'] else [],
                    "places_occupees": t['places_occupees'],
                    "places_libres": t['places_libres']
                }
                for t in tables
            ],
            "guests": [
                {
                    "id": u['id'],
                    "name": u['nom'],
                    "type": u['type_unite'],
                    "size": u['taille'],
                    "side": u['categorie'],
                    "relation_tag": u['relation_tag'],
                    "table_id": u['table_id'],
                    "table_name": u['table_nom']
                }
                for u in unites
            ]
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)
