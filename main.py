"""
Application principale - Gestion des Invitations
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                            QDateEdit, QTimeEdit, QFileDialog, QMessageBox, QSpinBox,
                            QHeaderView, QFrame, QProgressBar, QTextEdit, QDialog)
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
        
        self.setWindowTitle("🎊 Gestion des Invitations - Système Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # En-tête de l'application
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setStyleSheet("""
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2E86AB, stop:0.5 #1a5a7d, stop:1 #144461);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        titre_app = QLabel("🎊 GESTION DES INVITATIONS")
        titre_app.setStyleSheet("color: white; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        header_layout.addWidget(titre_app)
        
        header_layout.addStretch()
        
        date_label = QLabel("📅 " + datetime.now().strftime("%d/%m/%Y") + "  🕐 " + datetime.now().strftime("%H:%M"))
        date_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(date_label)
        
        main_layout.addWidget(header)
        
        # Widget avec onglets
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
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
        
        self.event_id_en_cours = None  # Pour stocker l'ID lors de la modification
        
        btn_ajouter = QPushButton("➕ Ajouter")
        btn_ajouter.clicked.connect(self.ajouter_evenement)
        form.addWidget(btn_ajouter)
        
        layout.addLayout(form)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        
        btn_modifier = QPushButton("✏️ Modifier l'événement sélectionné")
        btn_modifier.clicked.connect(self.preparer_modification_evenement)
        btn_modifier.setStyleSheet(f"background-color: {COLOR_WARNING}; color: white; padding: 8px;")
        actions_layout.addWidget(btn_modifier)
        
        btn_supprimer = QPushButton("🗑️ Supprimer l'événement sélectionné")
        btn_supprimer.clicked.connect(self.supprimer_evenement)
        btn_supprimer.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; padding: 8px;")
        actions_layout.addWidget(btn_supprimer)
        
        layout.addLayout(actions_layout)
        
        # Tableau des événements
        self.table_events = QTableWidget()
        self.table_events.setColumnCount(7)
        self.table_events.setHorizontalHeaderLabels([
            "ID", "Nom", "Date", "Heure", "Lieu", "Organisateur", "Template"
        ])
        self.table_events.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_events.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_events.itemSelectionChanged.connect(self.on_event_selected)
        self.table_events.cellClicked.connect(self.on_table_cell_clicked)
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
        
        self.invite_civilite = QComboBox()
        self.invite_civilite.addItems(["Mr", "Mme", "Couple", "Groupe", "Amis"])
        form.addWidget(self.invite_civilite)
        
        self.invite_nom_complet = QLineEdit()
        self.invite_nom_complet.setPlaceholderText("Nom complet de(s) invité(s)")
        self.invite_nom_complet.setMinimumWidth(200)
        form.addWidget(self.invite_nom_complet)
        
        self.invite_table = QComboBox()
        self.invite_table.setPlaceholderText("Sélectionner une table")
        self.invite_table.addItem("(Aucune table)", None)
        form.addWidget(self.invite_table)
        
        btn_gerer_tables = QPushButton("📋")
        btn_gerer_tables.setToolTip("Gérer les tables")
        btn_gerer_tables.setMaximumWidth(40)
        btn_gerer_tables.clicked.connect(self.ouvrir_gestion_tables)
        form.addWidget(btn_gerer_tables)
        
        self.invite_email = QLineEdit()
        self.invite_email.setPlaceholderText("Email (optionnel)")
        form.addWidget(self.invite_email)
        
        self.invite_tel = QLineEdit()
        self.invite_tel.setPlaceholderText("Téléphone (optionnel)")
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
        
        btn_affecter_categorie = QPushButton("🎯")
        btn_affecter_categorie.setToolTip("Affecter une catégorie à une table")
        btn_affecter_categorie.setMaximumWidth(40)
        btn_affecter_categorie.clicked.connect(self.affecter_categorie_table)
        form.addWidget(btn_affecter_categorie)
        
        layout.addLayout(form)
        
        # Tableau des invités
        self.table_invites = QTableWidget()
        self.table_invites.setColumnCount(9)
        self.table_invites.setHorizontalHeaderLabels([
            "ID", "Civilité", "Nom complet", "Table", "Email", "Téléphone", 
            "Catégorie", "Accompagnants", "Statut"
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
    
    def ajouter_evenement(self):
        """Ajouter un nouvel événement ou modifier un existant"""
        nom = self.event_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'événement est requis")
            return
        
        date = self.event_date.date().toString("yyyy-MM-dd")
        heure = self.event_heure.time().toString("HH:mm")
        lieu = self.event_lieu.text().strip()
        organisateur = self.event_organisateur.text().strip()
        
        # Vérifier si on est en mode modification
        if self.event_id_en_cours:
            # Mode modification
            success = self.db.modifier_evenement(
                self.event_id_en_cours, nom, date, heure, lieu, organisateur
            )
            if success:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' modifié!")
                self.event_id_en_cours = None
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la modification")
        else:
            # Mode ajout
            event_id = self.db.ajouter_evenement(
                nom, date, heure, lieu, organisateur
            )
            if event_id:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' ajouté!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
        
        # Réinitialiser le formulaire
        self.event_nom.clear()
        self.event_lieu.clear()
        self.event_organisateur.clear()
        self.event_id_en_cours = None
        self.rafraichir_evenements()
    
    def preparer_modification_evenement(self):
        """Préparer le formulaire pour modifier l'événement sélectionné"""
        selected = self.table_events.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement à modifier")
            return
        
        row = selected[0].row()
        event_id = int(self.table_events.item(row, 0).text())
        
        # Récupérer les données de l'événement
        event = self.db.obtenir_evenement(event_id)
        if not event:
            QMessageBox.critical(self, "Erreur", "Événement introuvable")
            return
        
        # Remplir le formulaire avec les données existantes
        self.event_id_en_cours = event_id
        self.event_nom.setText(event['nom'])
        self.event_date.setDate(QDate.fromString(event['date'], "yyyy-MM-dd"))
        self.event_heure.setTime(QTime.fromString(event['heure'], "HH:mm"))
        self.event_lieu.setText(event['lieu'] or '')
        self.event_organisateur.setText(event['organisateur'] or '')
        
        QMessageBox.information(self, "Mode Modification", 
                               f"Vous êtes en mode modification pour l'événement '{event['nom']}'.\n\n"
                               "Modifiez les champs souhaités puis cliquez sur 'Ajouter' pour enregistrer.\n"
                               "Pour modifier le template, utilisez la colonne Template dans le tableau.")
    
    def supprimer_evenement(self):
        """Supprimer l'événement sélectionné"""
        selected = self.table_events.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement à supprimer")
            return
        
        row = selected[0].row()
        event_id = int(self.table_events.item(row, 0).text())
        event_nom = self.table_events.item(row, 1).text()
        
        # Demander confirmation
        reponse = QMessageBox.question(
            self, "Confirmation", 
            f"Êtes-vous sûr de vouloir supprimer l'événement '{event_nom}' ?\n\n"
            "⚠️ ATTENTION: Tous les invités associés seront également supprimés!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            success = self.db.supprimer_evenement(event_id)
            if success:
                QMessageBox.information(self, "Succès", f"Événement '{event_nom}' supprimé!")
                self.rafraichir_evenements()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression")
    
    def changer_template_evenement(self, event_id, dialog):
        """Changer le template d'un événement existant"""
        try:
            fichier, _ = SimpleFileSelector.get_open_filename(
                self, "Choisir un nouveau template", str(TEMPLATES_DIR),
                "Images"
            )
            if fichier:
                # Récupérer l'événement
                event = self.db.obtenir_evenement(event_id)
                if event:
                    # Mettre à jour le template
                    success = self.db.modifier_evenement(
                        event_id, 
                        event['nom'], 
                        event['date'], 
                        event['heure'], 
                        event['lieu'], 
                        event['organisateur'] or '',
                        template_path=fichier
                    )
                    if success:
                        from pathlib import Path
                        QMessageBox.information(self, "Succès", 
                                              f"Template mis à jour !\n\n"
                                              f"Nouveau template : {Path(fichier).name}")
                        self.rafraichir_evenements()
                        dialog.close()
                    else:
                        QMessageBox.critical(self, "Erreur", "Erreur lors de la mise à jour")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
            print(f"Erreur changer_template_evenement: {e}")
            import traceback
            traceback.print_exc()
    
    def editer_template_evenement(self, event_id, template_path, dialog):
        """Éditer le template d'un événement"""
        try:
            if not template_path:
                QMessageBox.warning(self, "Aucun template", "Cet événement n'a pas de template.")
                return
            
            from pathlib import Path
            if not Path(template_path).exists():
                QMessageBox.warning(self, "Fichier introuvable", 
                                  f"Le template n'existe plus :\n{template_path}\n\n"
                                  "Veuillez choisir un nouveau template.")
                return
            
            # Fermer le dialogue
            dialog.close()
            
            # Ouvrir l'éditeur
            editor = TemplateEditorDialog(parent=self)
            editor.load_template(template_path)
            editor.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
            print(f"Erreur editer_template_evenement: {e}")
            import traceback
            traceback.print_exc()
    
    def voir_template(self, template_path):
        """Afficher le template dans une fenêtre"""
        try:
            from pathlib import Path
            if not Path(template_path).exists():
                QMessageBox.warning(self, "Fichier introuvable", 
                                  f"Le template n'existe plus :\n{template_path}")
                return
            
            # Créer un dialogue pour afficher l'image
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Aperçu - {Path(template_path).name}")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout()
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            label = QLabel()
            pixmap = QPixmap(str(template_path))
            
            # Redimensionner si trop grand
            if pixmap.width() > 1200 or pixmap.height() > 800:
                pixmap = pixmap.scaled(1200, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            
            scroll.setWidget(label)
            layout.addWidget(scroll)
            
            btn_fermer = QPushButton("Fermer")
            btn_fermer.clicked.connect(dialog.close)
            layout.addWidget(btn_fermer)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'affichage:\n{str(e)}")
            print(f"Erreur voir_template: {e}")
            import traceback
            traceback.print_exc()
    
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
            
            # Colonne template avec style cliquable
            template_item = QTableWidgetItem(event['template_path'] or '❌ Aucun')
            if event['template_path']:
                from pathlib import Path
                nom_fichier = Path(event['template_path']).name
                template_item.setText(f"🖼️ {nom_fichier}")
                template_item.setForeground(QColor("#2E86AB"))
                template_item.setToolTip("Cliquez pour modifier le template")
            else:
                template_item.setForeground(QColor("#D62246"))
                template_item.setToolTip("Cliquez pour ajouter un template")
            
            # Rendre la cellule cliquable visuellement
            font = template_item.font()
            font.setUnderline(True)
            template_item.setFont(font)
            
            self.table_events.setItem(i, 6, template_item)
        
        # Mettre à jour les combos
        self.combo_events.clear()
        self.combo_events_gen.clear()
        self.combo_events_stats.clear()
        
        for event in events:
            text = f"{event['nom']} - {event['date']}"
            self.combo_events.addItem(text, event['id'])
            self.combo_events_gen.addItem(text, event['id'])
            self.combo_events_stats.addItem(text, event['id'])
    
    def on_table_cell_clicked(self, row, column):
        """Gérer le clic sur une cellule du tableau"""
        # Colonne 6 = Template
        if column == 6:
            event_id = int(self.table_events.item(row, 0).text())
            event_nom = self.table_events.item(row, 1).text()
            
            # Afficher un dialogue pour choisir l'action
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Template - {event_nom}")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout()
            
            # Titre
            titre = QLabel(f"<h3>Gestion du template</h3>")
            titre.setAlignment(Qt.AlignCenter)
            layout.addWidget(titre)
            
            # Info événement
            info = QLabel(f"<b>Événement :</b> {event_nom}")
            layout.addWidget(info)
            
            # Boutons d'action
            btn_choisir = QPushButton("📁 Choisir/Changer le template")
            btn_choisir.setStyleSheet("background-color: #2E86AB; color: white; padding: 10px; font-size: 14px;")
            btn_choisir.clicked.connect(lambda: self.changer_template_evenement(event_id, dialog))
            layout.addWidget(btn_choisir)
            
            # Récupérer le template actuel
            event = self.db.obtenir_evenement(event_id)
            if event and event['template_path']:
                btn_editer = QPushButton("🎨 Éditer le template actuel")
                btn_editer.setStyleSheet("background-color: #F77F00; color: white; padding: 10px; font-size: 14px;")
                btn_editer.clicked.connect(lambda: self.editer_template_evenement(event_id, event['template_path'], dialog))
                layout.addWidget(btn_editer)
                
                btn_voir = QPushButton("👁️ Voir le template")
                btn_voir.setStyleSheet("background-color: #06A77D; color: white; padding: 10px; font-size: 14px;")
                btn_voir.clicked.connect(lambda: self.voir_template(event['template_path']))
                layout.addWidget(btn_voir)
            
            btn_annuler = QPushButton("Annuler")
            btn_annuler.clicked.connect(dialog.close)
            layout.addWidget(btn_annuler)
            
            dialog.setLayout(layout)
            dialog.exec_()
    
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
    
    # ============= TABLES =============
    
    def rafraichir_tables(self):
        """Rafraîchir la liste des tables disponibles pour l'événement sélectionné"""
        self.invite_table.clear()
        self.invite_table.addItem("(Aucune table)", None)
        
        if self.combo_events.currentIndex() < 0:
            return
        
        event_id = self.combo_events.currentData()
        tables = self.db.obtenir_tables_avec_places(event_id)
        
        # Grouper par côté
        tables_marie = [t for t in tables if t['cote'] == 'Marié']
        tables_mariee = [t for t in tables if t['cote'] == 'Mariée']
        
        # Ajouter les tables du marié
        if tables_marie:
            self.invite_table.addItem("--- Côté Marié ---", None)
            for table in tables_marie:
                places_occupees = table['places_occupees']
                capacite = table['capacite']
                places_dispo = capacite - places_occupees
                
                if places_dispo > 0:
                    text = f"{table['nom_table']} ({places_dispo}/{capacite} disponibles)"
                    self.invite_table.addItem(text, table['id'])
                else:
                    text = f"{table['nom_table']} (COMPLET {places_occupees}/{capacite})"
                    # Ajouter mais désactiver l'item
                    index = self.invite_table.count()
                    self.invite_table.addItem(text, table['id'])
                    item = self.invite_table.model().item(index)
                    item.setEnabled(False)
        
        # Ajouter les tables de la mariée
        if tables_mariee:
            self.invite_table.addItem("--- Côté Mariée ---", None)
            for table in tables_mariee:
                places_occupees = table['places_occupees']
                capacite = table['capacite']
                places_dispo = capacite - places_occupees
                
                if places_dispo > 0:
                    text = f"{table['nom_table']} ({places_dispo}/{capacite} disponibles)"
                    self.invite_table.addItem(text, table['id'])
                else:
                    text = f"{table['nom_table']} (COMPLET {places_occupees}/{capacite})"
                    # Ajouter mais désactiver l'item
                    index = self.invite_table.count()
                    self.invite_table.addItem(text, table['id'])
                    item = self.invite_table.model().item(index)
                    item.setEnabled(False)
    
    def ouvrir_gestion_tables(self):
        """Ouvrir la fenêtre de gestion des tables"""
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events.currentData()
        event = self.db.obtenir_evenement(event_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Gestion des tables - {event['nom']}")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel(f"Tables pour: {event['nom']}")
        titre.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titre)
        
        # Formulaire d'ajout de table
        form = QHBoxLayout()
        
        nom_table_input = QLineEdit()
        nom_table_input.setPlaceholderText("Nom de la table")
        form.addWidget(nom_table_input)
        
        cote_input = QComboBox()
        cote_input.addItems(["Marié", "Mariée"])
        form.addWidget(cote_input)
        
        capacite_input = QSpinBox()
        capacite_input.setPrefix("Capacité: ")
        capacite_input.setMinimum(1)
        capacite_input.setMaximum(50)
        capacite_input.setValue(10)
        form.addWidget(capacite_input)
        
        btn_ajouter_table = QPushButton("➕ Ajouter")
        form.addWidget(btn_ajouter_table)
        
        layout.addLayout(form)
        
        # Tableau des tables
        table_widget = QTableWidget()
        table_widget.setColumnCount(6)
        table_widget.setHorizontalHeaderLabels(["ID", "Nom", "Côté", "Occupé", "Capacité", "Actions"])
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table_widget)
        
        def rafraichir_liste_tables():
            """Rafraîchir le tableau des tables"""
            tables = self.db.obtenir_tables_avec_places(event_id)
            table_widget.setRowCount(len(tables))
            
            for i, table in enumerate(tables):
                places_occupees = table['places_occupees']
                capacite = table['capacite']
                
                table_widget.setItem(i, 0, QTableWidgetItem(str(table['id'])))
                table_widget.setItem(i, 1, QTableWidgetItem(table['nom_table']))
                table_widget.setItem(i, 2, QTableWidgetItem(table['cote']))
                
                # Places occupées avec couleur
                occupees_item = QTableWidgetItem(str(places_occupees))
                if places_occupees >= capacite:
                    occupees_item.setForeground(QColor("#D62246"))  # Rouge si complet
                elif places_occupees >= capacite * 0.8:
                    occupees_item.setForeground(QColor("#F77F00"))  # Orange si presque complet
                else:
                    occupees_item.setForeground(QColor("#06A77D"))  # Vert
                table_widget.setItem(i, 3, occupees_item)
                
                table_widget.setItem(i, 4, QTableWidgetItem(str(capacite)))
                
                # Bouton supprimer
                btn_supp = QPushButton("🗑️")
                btn_supp.setMaximumWidth(40)
                btn_supp.clicked.connect(lambda checked, tid=table['id']: supprimer_table(tid))
                table_widget.setCellWidget(i, 5, btn_supp)
        
        def ajouter_table():
            """Ajouter une nouvelle table"""
            nom = nom_table_input.text().strip()
            if not nom:
                QMessageBox.warning(dialog, "Erreur", "Le nom de la table est requis")
                return
            
            cote = cote_input.currentText()
            capacite = capacite_input.value()
            
            table_id = self.db.ajouter_table(event_id, nom, cote, capacite)
            if table_id:
                nom_table_input.clear()
                rafraichir_liste_tables()
                self.rafraichir_tables()
            else:
                QMessageBox.critical(dialog, "Erreur", "Erreur lors de l'ajout")
        
        def supprimer_table(table_id):
            """Supprimer une table"""
            rep = QMessageBox.question(dialog, "Confirmation", 
                                      "Voulez-vous vraiment supprimer cette table ?",
                                      QMessageBox.Yes | QMessageBox.No)
            if rep == QMessageBox.Yes:
                success = self.db.supprimer_table(table_id)
                if success:
                    rafraichir_liste_tables()
                    self.rafraichir_tables()
                else:
                    QMessageBox.critical(dialog, "Erreur", "Erreur lors de la suppression")
        
        btn_ajouter_table.clicked.connect(ajouter_table)
        
        # Bouton fermer
        btn_fermer = QPushButton("Fermer")
        btn_fermer.clicked.connect(dialog.close)
        layout.addWidget(btn_fermer)
        
        dialog.setLayout(layout)
        
        # Charger la liste initiale
        rafraichir_liste_tables()
        
        dialog.exec_()
    
    def affecter_categorie_table(self):
        """Affecter automatiquement tous les invités d'une catégorie à une table"""
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events.currentData()
        
        # Créer le dialogue
        dialog = QDialog(self)
        dialog.setWindowTitle("Affectation de catégorie à une table")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        titre = QLabel("Affecter tous les invités d'une catégorie à une table")
        titre.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(titre)
        
        # Formulaire
        form = QHBoxLayout()
        
        form.addWidget(QLabel("Catégorie:"))
        categorie_combo = QComboBox()
        categorie_combo.addItems(["Standard", "VIP", "Presse", "Invité spécial"])
        form.addWidget(categorie_combo)
        
        form.addWidget(QLabel("Table:"))
        table_combo = QComboBox()
        tables = self.db.obtenir_tables_avec_places(event_id)
        for table in tables:
            places_occupees = table['places_occupees']
            capacite = table['capacite']
            places_dispo = capacite - places_occupees
            text = f"{table['nom_table']} - {table['cote']} ({places_dispo}/{capacite} disponibles)"
            table_combo.addItem(text, table['id'])
        form.addWidget(table_combo)
        
        layout.addLayout(form)
        
        # Info
        info_label = QLabel("Cette action affectera tous les invités de la catégorie sélectionnée\n"
                           "qui n'ont pas encore de table assignée.")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
        # Compteur
        compteur_label = QLabel()
        layout.addWidget(compteur_label)
        
        def mettre_a_jour_compteur():
            """Mettre à jour le compteur d'invités sans table"""
            categorie = categorie_combo.currentText()
            invites = self.db.obtenir_invites(event_id)
            
            # Compter les invités de cette catégorie sans table
            invites_sans_table = [i for i in invites 
                                 if i['categorie'] == categorie and i['nom_table'] is None]
            
            total_places = sum(1 + i['nombre_accompagnants'] for i in invites_sans_table)
            
            compteur_label.setText(f"📊 {len(invites_sans_table)} invité(s) sans table "
                                  f"({total_places} place(s) nécessaires)")
            
            # Vérifier la capacité de la table sélectionnée
            if table_combo.currentIndex() >= 0:
                table_id = table_combo.currentData()
                result = self.db.verifier_capacite_table(table_id)
                if result:
                    _, _, places_dispo = result
                    if total_places > places_dispo:
                        compteur_label.setText(compteur_label.text() + 
                                             f"\n⚠️ ATTENTION: La table n'a que {places_dispo} place(s) disponible(s)")
                        compteur_label.setStyleSheet("color: #D62246; font-weight: bold;")
                    else:
                        compteur_label.setStyleSheet("color: #06A77D; font-weight: bold;")
        
        categorie_combo.currentIndexChanged.connect(mettre_a_jour_compteur)
        table_combo.currentIndexChanged.connect(mettre_a_jour_compteur)
        mettre_a_jour_compteur()
        
        # Boutons
        boutons = QHBoxLayout()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.clicked.connect(dialog.close)
        boutons.addWidget(btn_annuler)
        
        btn_affecter = QPushButton("✓ Affecter")
        btn_affecter.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: white; padding: 8px;")
        boutons.addWidget(btn_affecter)
        
        layout.addLayout(boutons)
        dialog.setLayout(layout)
        
        def executer_affectation():
            """Exécuter l'affectation"""
            categorie = categorie_combo.currentText()
            table_id = table_combo.currentData()
            
            if table_id is None:
                QMessageBox.warning(dialog, "Erreur", "Veuillez sélectionner une table")
                return
            
            # Récupérer les invités de cette catégorie sans table
            invites = self.db.obtenir_invites(event_id)
            invites_a_affecter = [i for i in invites 
                                 if i['categorie'] == categorie and i['nom_table'] is None]
            
            if not invites_a_affecter:
                QMessageBox.information(dialog, "Information", 
                                      "Aucun invité de cette catégorie sans table assignée.")
                return
            
            # Vérifier la capacité totale nécessaire
            total_places = sum(1 + i['nombre_accompagnants'] for i in invites_a_affecter)
            result = self.db.verifier_capacite_table(table_id)
            
            if result:
                _, _, places_dispo = result
                if total_places > places_dispo:
                    rep = QMessageBox.question(dialog, "Capacité dépassée",
                                              f"La table n'a que {places_dispo} place(s) disponible(s) "
                                              f"mais {total_places} place(s) sont nécessaires.\n\n"
                                              "Voulez-vous quand même continuer l'affectation ?",
                                              QMessageBox.Yes | QMessageBox.No)
                    if rep != QMessageBox.Yes:
                        return
            
            # Affecter les invités
            self.db.connect()
            nb_affectes = 0
            for invite in invites_a_affecter:
                self.db.cursor.execute('''
                    UPDATE invites SET table_id = ? WHERE id = ?
                ''', (table_id, invite['id']))
                nb_affectes += 1
            
            self.db.conn.commit()
            self.db.disconnect()
            
            QMessageBox.information(dialog, "Succès", 
                                  f"{nb_affectes} invité(s) de la catégorie '{categorie}' "
                                  f"ont été affectés à la table!")
            self.rafraichir_invites()
            dialog.close()
        
        btn_affecter.clicked.connect(executer_affectation)
        dialog.exec_()
    
    # ============= INVITÉS =============
    
    def ajouter_invite(self):
        """Ajouter un nouvel invité"""
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events.currentData()
        civilite = self.invite_civilite.currentText()
        nom_complet = self.invite_nom_complet.text().strip()
        
        if not nom_complet:
            QMessageBox.warning(self, "Erreur", "Le nom complet est requis")
            return
        
        table_id = self.invite_table.currentData()
        email = self.invite_email.text().strip()
        tel = self.invite_tel.text().strip()
        categorie = self.invite_categorie.currentText()
        accompagnants = self.invite_accompagnants.value()
        
        # Vérifier la capacité de la table si une table est sélectionnée
        if table_id is not None:
            result = self.db.verifier_capacite_table(table_id)
            if result:
                places_occupees, capacite_totale, places_disponibles = result
                places_requises = 1 + accompagnants
                
                if places_requises > places_disponibles:
                    QMessageBox.warning(self, "Capacité insuffisante", 
                                      f"La table sélectionnée n'a que {places_disponibles} place(s) disponible(s).\n"
                                      f"Vous essayez d'ajouter {places_requises} personne(s) (invité + {accompagnants} accompagnant(s)).\n\n"
                                      f"Places occupées: {places_occupees}/{capacite_totale}\n"
                                      f"Veuillez choisir une autre table ou réduire le nombre d'accompagnants.")
                    return
        
        invite_id = self.db.ajouter_invite(
            event_id, civilite, nom_complet, table_id, email, tel,
            nombre_accompagnants=accompagnants,
            categorie=categorie
        )
        
        if invite_id:
            QMessageBox.information(self, "Succès", f"Invité {nom_complet} ajouté!")
            self.invite_nom_complet.clear()
            self.invite_table.setCurrentIndex(0)
            self.invite_email.clear()
            self.invite_tel.clear()
            self.invite_accompagnants.setValue(0)
            self.rafraichir_invites()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
    
    def rafraichir_invites(self):
        """Rafraîchir la liste des invités"""
        # Rafraîchir d'abord la liste des tables
        self.rafraichir_tables()
        
        if self.combo_events.currentIndex() < 0:
            self.table_invites.setRowCount(0)
            return
        
        event_id = self.combo_events.currentData()
        invites = self.db.obtenir_invites(event_id)
        
        self.table_invites.setRowCount(len(invites))
        for i, invite in enumerate(invites):
            self.table_invites.setItem(i, 0, QTableWidgetItem(str(invite['id'])))
            self.table_invites.setItem(i, 1, QTableWidgetItem(invite['civilite']))
            self.table_invites.setItem(i, 2, QTableWidgetItem(invite['nom_complet']))
            self.table_invites.setItem(i, 3, QTableWidgetItem(invite['nom_table'] or ''))
            self.table_invites.setItem(i, 4, QTableWidgetItem(invite['email'] or ''))
            self.table_invites.setItem(i, 5, QTableWidgetItem(invite['telephone'] or ''))
            self.table_invites.setItem(i, 6, QTableWidgetItem(invite['categorie']))
            self.table_invites.setItem(i, 7, QTableWidgetItem(str(invite['nombre_accompagnants'])))
            self.table_invites.setItem(i, 8, QTableWidgetItem(invite['statut']))
            
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
                    'civilite': invite['civilite'],
                    'nom_complet': invite['nom_complet'],
                    'nom_table': invite['nom_table'],
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
                
                self.log_gen.append(f"✅ {invite['nom_complet']} - {path}")
                
            except Exception as e:
                self.log_gen.append(f"❌ Erreur pour {invite['nom_complet']}: {e}")
            
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
                    msg += f"Événement: {inv.get('nom_evenement', 'N/A')}\n"
                    msg += f"Invité: {inv['nom_complet']}\n"
                    msg += f"Table: {inv.get('nom_table') or 'Non assignée'}\n"
                    msg += f"Date: {inv.get('date_evenement', 'N/A')}\n"
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
                msg += f"Événement: {inv.get('nom_evenement', 'N/A')}\n"
                msg += f"Invité: {inv['nom_complet']}\n"
                msg += f"Table: {inv.get('nom_table') or 'Non assignée'}\n"
                msg += f"Date: {inv.get('date_evenement', 'N/A')}\n"
            
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
        """Appliquer le style global moderne"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }}
            
            QTabWidget::pane {{
                border: 2px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
                margin-top: -1px;
            }}
            
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                color: #495057;
                border: 1px solid #dee2e6;
                min-width: 120px;
            }}
            
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLOR_PRIMARY}, stop:1 #1a5a7d);
                color: white;
                border-bottom: 2px solid {COLOR_PRIMARY};
            }}
            
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }}
            
            QPushButton {{
                padding: 10px 20px;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLOR_PRIMARY}, stop:1 #1a5a7d);
                color: white;
                border: none;
                font-weight: bold;
                font-size: 13px;
                min-height: 35px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a5a7d, stop:1 #144461);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            
            QPushButton:pressed {{
                background: #144461;
                padding-top: 12px;
                padding-bottom: 8px;
            }}
            
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
                padding: 8px 12px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-height: 35px;
            }}
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {{
                border: 2px solid {COLOR_PRIMARY};
                background-color: #f8f9ff;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }}
            
            QTableWidget {{
                border: 2px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
                background-color: white;
                alternate-background-color: #f8f9fa;
                font-size: 13px;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }}
            
            QTableWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLOR_PRIMARY}, stop:1 #1a5a7d);
                color: white;
            }}
            
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #495057, stop:1 #343a40);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }}
            
            QProgressBar {{
                border: 2px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                background-color: #e9ecef;
                height: 25px;
                font-weight: bold;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLOR_SUCCESS}, stop:1 #04845b);
                border-radius: 4px;
            }}
            
            QTextEdit {{
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
            
            QLabel {{
                color: #212529;
                font-size: 13px;
            }}
            
            QFrame {{
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                border-radius: 3px;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #e9ecef;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
