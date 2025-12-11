"""
Application principale - Gestion des Invitations
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                            QDateEdit, QTimeEdit, QFileDialog, QMessageBox, QSpinBox,
                            QHeaderView, QFrame, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor
from pathlib import Path
from datetime import datetime

from database_model import InvitationModel
from invitation_generator import InvitationGenerator
from qr_scanner import QRScanner
from template_editor import TemplateEditorDialog
from template_editor_simple import TemplateEditorSimple
from simple_file_selector import SimpleFileSelector
from config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, TEMPLATES_DIR


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.db = InvitationModel()
        self.db.create_tables()
        
        self.setWindowTitle("Gestion des Invitations")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central avec onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Créer les onglets
        self.tab_evenements = self.creer_tab_evenements()
        self.tab_invites = self.creer_tab_invites()
        self.tab_generateur = self.creer_tab_generateur()
        self.tab_scanner = self.creer_tab_scanner()
        self.tab_stats = self.creer_tab_statistiques()
        
        # Ajouter les onglets
        self.tabs.addTab(self.tab_evenements, "📅 Événements")
        self.tabs.addTab(self.tab_invites, "👥 Invités")
        self.tabs.addTab(self.tab_generateur, "🎨 Générateur")
        self.tabs.addTab(self.tab_scanner, "📱 Scanner")
        self.tabs.addTab(self.tab_stats, "📊 Statistiques")
        
        # Appliquer le style
        self.appliquer_style()
        
        # Charger les données initiales
        self.rafraichir_evenements()
    
    def creer_tab_evenements(self):
        """Créer l'onglet de gestion des événements"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("Gestion des Événements")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)
        
        # Formulaire d'ajout
        form = QHBoxLayout()
        
        self.event_nom = QLineEdit()
        self.event_nom.setPlaceholderText("Nom de l'événement")
        form.addWidget(self.event_nom)
        
        self.event_date = QDateEdit()
        self.event_date.setDate(QDate.currentDate())
        self.event_date.setCalendarPopup(True)
        form.addWidget(self.event_date)
        
        self.event_heure = QTimeEdit()
        self.event_heure.setTime(QTime(19, 0))
        form.addWidget(self.event_heure)
        
        self.event_lieu = QLineEdit()
        self.event_lieu.setPlaceholderText("Lieu")
        form.addWidget(self.event_lieu)
        
        self.event_organisateur = QLineEdit()
        self.event_organisateur.setPlaceholderText("Organisateur")
        form.addWidget(self.event_organisateur)
        
        btn_template = QPushButton("📁 Template")
        btn_template.clicked.connect(self.choisir_template)
        form.addWidget(btn_template)
        
        btn_edit_template = QPushButton("🎨 Éditer Template")
        btn_edit_template.clicked.connect(self.editer_template)
        form.addWidget(btn_edit_template)
        
        self.template_path = None
        
        btn_ajouter = QPushButton("➕ Ajouter")
        btn_ajouter.clicked.connect(self.ajouter_evenement)
        form.addWidget(btn_ajouter)
        
        layout.addLayout(form)
        
        # Tableau des événements
        self.table_events = QTableWidget()
        self.table_events.setColumnCount(7)
        self.table_events.setHorizontalHeaderLabels([
            "ID", "Nom", "Date", "Heure", "Lieu", "Organisateur", "Template"
        ])
        self.table_events.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_events.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_events.itemSelectionChanged.connect(self.on_event_selected)
        layout.addWidget(self.table_events)
        
        tab.setLayout(layout)
        return tab
    
    def creer_tab_invites(self):
        """Créer l'onglet de gestion des invités"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Titre et sélecteur d'événement
        header = QHBoxLayout()
        titre = QLabel("Gestion des Invités")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        header.addWidget(titre)
        
        header.addStretch()
        
        header.addWidget(QLabel("Événement:"))
        self.combo_events = QComboBox()
        self.combo_events.currentIndexChanged.connect(self.rafraichir_invites)
        header.addWidget(self.combo_events)
        
        layout.addLayout(header)
        
        # Formulaire d'ajout
        form = QHBoxLayout()
        
        self.invite_nom = QLineEdit()
        self.invite_nom.setPlaceholderText("Nom")
        form.addWidget(self.invite_nom)
        
        self.invite_prenom = QLineEdit()
        self.invite_prenom.setPlaceholderText("Prénom")
        form.addWidget(self.invite_prenom)
        
        self.invite_email = QLineEdit()
        self.invite_email.setPlaceholderText("Email")
        form.addWidget(self.invite_email)
        
        self.invite_tel = QLineEdit()
        self.invite_tel.setPlaceholderText("Téléphone")
        form.addWidget(self.invite_tel)
        
        self.invite_categorie = QComboBox()
        self.invite_categorie.addItems(["Standard", "VIP", "Presse", "Invité spécial"])
        form.addWidget(self.invite_categorie)
        
        self.invite_accompagnants = QSpinBox()
        self.invite_accompagnants.setPrefix("Accomp.: ")
        self.invite_accompagnants.setMaximum(10)
        form.addWidget(self.invite_accompagnants)
        
        btn_ajouter_invite = QPushButton("➕ Ajouter Invité")
        btn_ajouter_invite.clicked.connect(self.ajouter_invite)
        form.addWidget(btn_ajouter_invite)
        
        layout.addLayout(form)
        
        # Tableau des invités
        self.table_invites = QTableWidget()
        self.table_invites.setColumnCount(9)
        self.table_invites.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Email", "Téléphone", "Catégorie", 
            "Accompagnants", "Statut", "QR Code"
        ])
        self.table_invites.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_invites.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table_invites)
        
        tab.setLayout(layout)
        return tab
    
    def creer_tab_generateur(self):
        """Créer l'onglet de génération d'invitations"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("Générateur d'Invitations")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)
        
        # Sélection événement
        selection = QHBoxLayout()
        selection.addWidget(QLabel("Événement:"))
        self.combo_events_gen = QComboBox()
        selection.addWidget(self.combo_events_gen)
        selection.addStretch()
        
        btn_generer = QPushButton("🎨 Générer toutes les invitations")
        btn_generer.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: white; padding: 10px; font-size: 14px;")
        btn_generer.clicked.connect(self.generer_invitations)
        selection.addWidget(btn_generer)
        
        layout.addLayout(selection)
        
        # Barre de progression
        self.progress_gen = QProgressBar()
        layout.addWidget(self.progress_gen)
        
        # Zone de log
        self.log_gen = QTextEdit()
        self.log_gen.setReadOnly(True)
        layout.addWidget(self.log_gen)
        
        tab.setLayout(layout)
        return tab
    
    def creer_tab_scanner(self):
        """Créer l'onglet de scan QR"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("Scanner de QR Codes")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)
        
        # Contrôles
        controls = QHBoxLayout()
        
        btn_start_scan = QPushButton("▶️ Démarrer Scanner")
        btn_start_scan.setStyleSheet(f"background-color: {COLOR_SUCCESS}; color: white; padding: 10px;")
        btn_start_scan.clicked.connect(self.demarrer_scanner)
        controls.addWidget(btn_start_scan)
        
        btn_stop_scan = QPushButton("⏹️ Arrêter Scanner")
        btn_stop_scan.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; padding: 10px;")
        btn_stop_scan.clicked.connect(self.arreter_scanner)
        controls.addWidget(btn_stop_scan)
        
        btn_scan_fichier = QPushButton("📁 Scanner un fichier")
        btn_scan_fichier.clicked.connect(self.scanner_fichier)
        controls.addWidget(btn_scan_fichier)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Zone de résultat
        self.scan_result = QTextEdit()
        self.scan_result.setReadOnly(True)
        self.scan_result.setFont(QFont("Monospace", 12))
        layout.addWidget(self.scan_result)
        
        # Statistiques en temps réel
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Box)
        stats_layout = QHBoxLayout()
        
        self.lbl_total_scans = QLabel("Scans: 0")
        self.lbl_total_scans.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.lbl_total_scans)
        
        self.lbl_presents = QLabel("Présents: 0")
        self.lbl_presents.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.lbl_presents)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        self.scanner = None
        
        tab.setLayout(layout)
        return tab
    
    def creer_tab_statistiques(self):
        """Créer l'onglet de statistiques"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("Statistiques")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)
        
        # Sélection événement
        selection = QHBoxLayout()
        selection.addWidget(QLabel("Événement:"))
        self.combo_events_stats = QComboBox()
        self.combo_events_stats.currentIndexChanged.connect(self.rafraichir_statistiques)
        selection.addWidget(self.combo_events_stats)
        selection.addStretch()
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.rafraichir_statistiques)
        selection.addWidget(btn_refresh)
        
        layout.addLayout(selection)
        
        # Cartes de statistiques
        cards = QHBoxLayout()
        
        # Total invités
        card1 = self.creer_card_stat("Total Invités", "0", COLOR_PRIMARY)
        cards.addWidget(card1)
        self.lbl_total_invites = card1.findChild(QLabel, "value")
        
        # Total personnes (avec accompagnants)
        card2 = self.creer_card_stat("Total Personnes", "0", COLOR_SUCCESS)
        cards.addWidget(card2)
        self.lbl_total_personnes = card2.findChild(QLabel, "value")
        
        # Présents
        card3 = self.creer_card_stat("Présents", "0", COLOR_WARNING)
        cards.addWidget(card3)
        self.lbl_stat_presents = card3.findChild(QLabel, "value")
        
        # Taux de présence
        card4 = self.creer_card_stat("Taux Présence", "0%", COLOR_DANGER)
        cards.addWidget(card4)
        self.lbl_taux_presence = card4.findChild(QLabel, "value")
        
        layout.addLayout(cards)
        
        # Tableau par catégorie
        self.table_categories = QTableWidget()
        self.table_categories.setColumnCount(4)
        self.table_categories.setHorizontalHeaderLabels([
            "Catégorie", "Nombre d'invités", "Personnes totales", "Présents"
        ])
        self.table_categories.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_categories)
        
        tab.setLayout(layout)
        return tab
    
    def creer_card_stat(self, titre, valeur, couleur):
        """Créer une carte de statistique"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet(f"background-color: white; border: 2px solid {couleur}; border-radius: 5px;")
        
        layout = QVBoxLayout()
        
        lbl_titre = QLabel(titre)
        lbl_titre.setAlignment(Qt.AlignCenter)
        lbl_titre.setFont(QFont("Arial", 12))
        layout.addWidget(lbl_titre)
        
        lbl_valeur = QLabel(valeur)
        lbl_valeur.setObjectName("value")
        lbl_valeur.setAlignment(Qt.AlignCenter)
        lbl_valeur.setFont(QFont("Arial", 24, QFont.Bold))
        lbl_valeur.setStyleSheet(f"color: {couleur};")
        layout.addWidget(lbl_valeur)
        
        frame.setLayout(layout)
        return frame
    
    # ============= ÉVÉNEMENTS =============
    
    def choisir_template(self):
        """Choisir un fichier template"""
        try:
            fichier, _ = SimpleFileSelector.get_open_filename(
                self, "Choisir un template", str(TEMPLATES_DIR),
                "Images"
            )
            if fichier:
                self.template_path = fichier
                QMessageBox.information(self, "Template", f"Template sélectionné:\n{fichier}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du choix du template:\n{str(e)}")
            print(f"Erreur choisir_template: {e}")
            import traceback
            traceback.print_exc()
    
    def editer_template(self):
        """Ouvrir l'éditeur de template"""
        try:
            print("=== Début editer_template ===")
            
            # Créer l'éditeur complet
            print("Création de l'éditeur...")
            editor = TemplateEditorDialog(parent=self)
            
            # Charger le template si déjà sélectionné
            if self.template_path:
                print(f"Chargement du template: {self.template_path}")
                editor.load_template(self.template_path)
            
            print("Affichage de l'éditeur...")
            editor.exec_()
            print("=== Fin editer_template ===")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture de l'éditeur:\n{str(e)}")
            print(f"ERREUR editer_template: {e}")
            import traceback
            traceback.print_exc()

    
    def ajouter_evenement(self):
        """Ajouter un nouvel événement"""
        nom = self.event_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'événement est requis")
            return
        
        date = self.event_date.date().toString("yyyy-MM-dd")
        heure = self.event_heure.time().toString("HH:mm")
        lieu = self.event_lieu.text().strip()
        organisateur = self.event_organisateur.text().strip()
        
        event_id = self.db.ajouter_evenement(
            nom, date, heure, lieu, organisateur,
            template_path=self.template_path
        )
        
        if event_id:
            QMessageBox.information(self, "Succès", f"Événement '{nom}' ajouté!")
            self.event_nom.clear()
            self.event_lieu.clear()
            self.event_organisateur.clear()
            self.template_path = None
            self.rafraichir_evenements()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
    
    def rafraichir_evenements(self):
        """Rafraîchir la liste des événements"""
        events = self.db.obtenir_evenements()
        
        self.table_events.setRowCount(len(events))
        for i, event in enumerate(events):
            self.table_events.setItem(i, 0, QTableWidgetItem(str(event['id'])))
            self.table_events.setItem(i, 1, QTableWidgetItem(event['nom']))
            self.table_events.setItem(i, 2, QTableWidgetItem(event['date']))
            self.table_events.setItem(i, 3, QTableWidgetItem(event['heure']))
            self.table_events.setItem(i, 4, QTableWidgetItem(event['lieu'] or ''))
            self.table_events.setItem(i, 5, QTableWidgetItem(event['organisateur'] or ''))
            self.table_events.setItem(i, 6, QTableWidgetItem(event['template_path'] or 'Aucun'))
        
        # Mettre à jour les combos
        self.combo_events.clear()
        self.combo_events_gen.clear()
        self.combo_events_stats.clear()
        
        for event in events:
            text = f"{event['nom']} - {event['date']}"
            self.combo_events.addItem(text, event['id'])
            self.combo_events_gen.addItem(text, event['id'])
            self.combo_events_stats.addItem(text, event['id'])
    
    def on_event_selected(self):
        """Quand un événement est sélectionné"""
        selected = self.table_events.selectedItems()
        if selected:
            row = selected[0].row()
            event_id = int(self.table_events.item(row, 0).text())
            # Mettre à jour le combo des invités
            index = self.combo_events.findData(event_id)
            if index >= 0:
                self.combo_events.setCurrentIndex(index)
    
    # ============= INVITÉS =============
    
    def ajouter_invite(self):
        """Ajouter un nouvel invité"""
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events.currentData()
        nom = self.invite_nom.text().strip()
        prenom = self.invite_prenom.text().strip()
        
        if not nom or not prenom:
            QMessageBox.warning(self, "Erreur", "Nom et prénom requis")
            return
        
        email = self.invite_email.text().strip()
        tel = self.invite_tel.text().strip()
        categorie = self.invite_categorie.currentText()
        accompagnants = self.invite_accompagnants.value()
        
        invite_id = self.db.ajouter_invite(
            event_id, nom, prenom, email, tel,
            nombre_accompagnants=accompagnants,
            categorie=categorie
        )
        
        if invite_id:
            QMessageBox.information(self, "Succès", f"Invité {prenom} {nom} ajouté!")
            self.invite_nom.clear()
            self.invite_prenom.clear()
            self.invite_email.clear()
            self.invite_tel.clear()
            self.invite_accompagnants.setValue(0)
            self.rafraichir_invites()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
    
    def rafraichir_invites(self):
        """Rafraîchir la liste des invités"""
        if self.combo_events.currentIndex() < 0:
            self.table_invites.setRowCount(0)
            return
        
        event_id = self.combo_events.currentData()
        invites = self.db.obtenir_invites(event_id)
        
        self.table_invites.setRowCount(len(invites))
        for i, invite in enumerate(invites):
            self.table_invites.setItem(i, 0, QTableWidgetItem(str(invite['id'])))
            self.table_invites.setItem(i, 1, QTableWidgetItem(invite['nom']))
            self.table_invites.setItem(i, 2, QTableWidgetItem(invite['prenom']))
            self.table_invites.setItem(i, 3, QTableWidgetItem(invite['email'] or ''))
            self.table_invites.setItem(i, 4, QTableWidgetItem(invite['telephone'] or ''))
            self.table_invites.setItem(i, 5, QTableWidgetItem(invite['categorie']))
            self.table_invites.setItem(i, 6, QTableWidgetItem(str(invite['nombre_accompagnants'])))
            self.table_invites.setItem(i, 7, QTableWidgetItem(invite['statut']))
            self.table_invites.setItem(i, 8, QTableWidgetItem(invite['qr_code'] or ''))
            
            # Colorer selon le statut
            if invite['statut'] == 'présent':
                for col in range(9):
                    self.table_invites.item(i, col).setBackground(QColor(COLOR_SUCCESS))
    
    # ============= GÉNÉRATEUR =============
    
    def generer_invitations(self):
        """Générer les invitations pour un événement"""
        if self.combo_events_gen.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events_gen.currentData()
        event = self.db.obtenir_evenement(event_id)
        invites = self.db.obtenir_invites(event_id)
        
        if not invites:
            QMessageBox.warning(self, "Attention", "Aucun invité pour cet événement")
            return
        
        # Initialiser le générateur
        generator = InvitationGenerator(template_path=event['template_path'])
        
        self.log_gen.clear()
        self.log_gen.append(f"🎨 Génération de {len(invites)} invitations...")
        self.progress_gen.setMaximum(len(invites))
        self.progress_gen.setValue(0)
        
        # Générer chaque invitation
        for i, invite in enumerate(invites):
            try:
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
                
                path, qr_code = generator.creer_invitation(invite_data)
                
                # Mettre à jour la base de données
                self.db.mettre_a_jour_invite(
                    invite['id'],
                    qr_code=qr_code,
                    invitation_path=path
                )
                
                self.log_gen.append(f"✅ {invite['prenom']} {invite['nom']} - {path}")
                
            except Exception as e:
                self.log_gen.append(f"❌ Erreur pour {invite['prenom']} {invite['nom']}: {e}")
            
            self.progress_gen.setValue(i + 1)
            QApplication.processEvents()
        
        self.log_gen.append(f"\n✨ Génération terminée!")
        QMessageBox.information(self, "Succès", f"{len(invites)} invitations générées!")
        self.rafraichir_invites()
    
    # ============= SCANNER =============
    
    def demarrer_scanner(self):
        """Démarrer le scanner QR"""
        try:
            self.scanner = QRScanner()
            self.scan_result.append("🎥 Scanner démarré...\n")
            
            # Scanner dans un thread séparé (simplifié ici)
            QMessageBox.information(self, "Scanner", 
                "Le scanner démarre dans une fenêtre séparée.\nAppuyez sur 'Q' pour quitter.")
            
            def on_scan(qr_data, validation):
                msg = f"\n{'='*50}\n"
                msg += f"📱 QR: {qr_data}\n"
                msg += f"{validation['message']}\n"
                if validation['invite']:
                    inv = validation['invite']
                    msg += f"Invité: {inv['prenom']} {inv['nom']}\n"
                    msg += f"Catégorie: {inv['categorie']}\n"
                    if 'nb_personnes' in validation:
                        msg += f"Personnes: {validation['nb_personnes']}\n"
                self.scan_result.append(msg)
                self.rafraichir_statistiques()
            
            self.scanner.scanner_en_continu(callback=on_scan)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de démarrer le scanner:\n{e}")
    
    def arreter_scanner(self):
        """Arrêter le scanner"""
        if self.scanner:
            self.scanner.arreter_camera()
            self.scan_result.append("\n⏹️ Scanner arrêté\n")
    
    def scanner_fichier(self):
        """Scanner un QR code depuis un fichier"""
        fichier, _ = SimpleFileSelector.get_open_filename(
            self, "Choisir une image", str(TEMPLATES_DIR),
            "Images"
        )
        
        if fichier:
            scanner = QRScanner()
            validation = scanner.scanner_fichier_image(fichier)
            
            msg = f"\n{'='*50}\n"
            msg += f"📁 Fichier: {fichier}\n"
            msg += f"{validation['message']}\n"
            if validation['invite']:
                inv = validation['invite']
                msg += f"Invité: {inv['prenom']} {inv['nom']}\n"
                msg += f"Catégorie: {inv['categorie']}\n"
            
            self.scan_result.append(msg)
            self.rafraichir_statistiques()
    
    # ============= STATISTIQUES =============
    
    def rafraichir_statistiques(self):
        """Rafraîchir les statistiques"""
        if self.combo_events_stats.currentIndex() < 0:
            return
        
        event_id = self.combo_events_stats.currentData()
        stats = self.db.obtenir_statistiques(event_id)
        
        # Mettre à jour les cartes
        self.lbl_total_invites.setText(str(stats['total_invites']))
        self.lbl_total_personnes.setText(str(stats['total_personnes']))
        self.lbl_stat_presents.setText(f"{stats['presents']}/{stats['personnes_presentes']}")
        self.lbl_taux_presence.setText(f"{stats['taux_presence']:.1f}%")
        
        # Mettre à jour le tableau par catégorie
        categories = stats['par_categorie']
        self.table_categories.setRowCount(len(categories))
        
        for i, (cat, data) in enumerate(categories.items()):
            self.table_categories.setItem(i, 0, QTableWidgetItem(cat))
            self.table_categories.setItem(i, 1, QTableWidgetItem(str(data['nombre'])))
            self.table_categories.setItem(i, 2, QTableWidgetItem(str(data['total_personnes'])))
            self.table_categories.setItem(i, 3, QTableWidgetItem(str(data['presents'])))
    
    def appliquer_style(self):
        """Appliquer le style global"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
            }}
            QTabWidget::pane {{
                border: 1px solid #ddd;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #236B8E;
            }}
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            QTableWidget {{
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
