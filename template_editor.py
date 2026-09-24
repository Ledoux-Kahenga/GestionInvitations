"""
Éditeur visuel de template d'invitation
Permet de positionner les éléments (textes, QR code) sur le template
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QScrollArea, QWidget, QComboBox, QSpinBox,
                            QGroupBox, QFormLayout, QColorDialog, QFileDialog,
                            QMessageBox, QLineEdit, QMenuBar, QMenu, QAction,
                            QShortcut, QCheckBox)
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage, QKeySequence
from PIL import Image, ImageFont
import json
from pathlib import Path
import os
import copy
from config import TEMPLATES_DIR, FONTS_DIR
from simple_file_selector import SimpleFileSelector


class DraggableElement(QLabel):
    """Élément déplaçable sur le canvas (zone de texte ou QR code)"""
    
    def __init__(self, element_type, name, parent=None, editor=None):
        super().__init__(parent)
        self.element_type = element_type  # 'text' ou 'qr'
        self.name = name
        self.dragging = False
        self.offset = QPoint()
        self.canvas_parent = parent
        self.editor = editor  # Référence vers l'éditeur principal
        self.element_data = None  # Référence vers les données de l'élément
        
        # Permettre le focus clavier
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Style visuel
        self.is_selected = False
        self.update_style()
        self.update_label()
        
        # Alignement selon le type
        if element_type == 'qr':
            self.setAlignment(Qt.AlignCenter)
            self.resize(200, 200)
        else:
            # Pour le texte: alignement à gauche et en bas (comme dans le générateur final)
            self.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
            # Largeur minimale pour faciliter le positionnement précis
            self.resize(20, 40)
        
        self.setCursor(Qt.OpenHandCursor)
    
    def update_label(self):
        """Mettre à jour le label avec les coordonnées et dimensions"""
        if self.canvas_parent and hasattr(self.canvas_parent, 'scale_factor'):
            scale = self.canvas_parent.scale_factor
            if scale > 0:
                real_x = round(self.x() / scale)
                real_y = round(self.y() / scale)
                real_width = round(self.width() / scale)
                real_height = round(self.height() / scale)
                self.setText(f"{self.name} ({real_x},{real_y}) {real_width}×{real_height}")
                return
        self.setText(self.name)
    
    def update_style(self):
        """Mettre à jour le style visuel selon l'état de sélection"""
        if self.is_selected:
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(231, 76, 60, 150);
                    border: 3px solid #E74C3C;
                    border-radius: 0px;
                    color: white;
                    padding: 0px;
                    margin: 0px;
                    font-weight: bold;
                    font-size: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: rgba(46, 134, 171, 100);
                    border: 2px dashed #2E86AB;
                    border-radius: 0px;
                    color: white;
                    padding: 0px;
                    margin: 0px;
                    font-weight: bold;
                    font-size: 10px;
                }
            """)
    
    def set_selected(self, selected):
        """Définir l'état de sélection"""
        self.is_selected = selected
        self.update_style()
        if selected:
            self.setFocus()  # Prendre le focus quand sélectionné
    
    def keyPressEvent(self, event):
        """Gérer les touches directionnelles pour déplacer l'élément"""
        step = 10 if event.modifiers() & Qt.ShiftModifier else 1  # Shift = déplacement rapide
        
        # Sauvegarder la position de départ au premier déplacement
        if not hasattr(self, 'key_move_start_pos'):
            self.key_move_start_pos = None
        
        new_x = self.x()
        new_y = self.y()
        handled = False
        
        if event.key() == Qt.Key_Left:
            if self.key_move_start_pos is None:
                self.key_move_start_pos = self.pos()
            new_x = max(0, self.x() - step)
            handled = True
        elif event.key() == Qt.Key_Right:
            if self.key_move_start_pos is None:
                self.key_move_start_pos = self.pos()
            parent_rect = self.parent().rect()
            new_x = min(self.x() + step, parent_rect.width() - self.width())
            handled = True
        elif event.key() == Qt.Key_Up:
            if self.key_move_start_pos is None:
                self.key_move_start_pos = self.pos()
            new_y = max(0, self.y() - step)
            handled = True
        elif event.key() == Qt.Key_Down:
            if self.key_move_start_pos is None:
                self.key_move_start_pos = self.pos()
            parent_rect = self.parent().rect()
            new_y = min(self.y() + step, parent_rect.height() - self.height())
            handled = True
        elif event.key() == Qt.Key_Delete:
            # Supprimer l'élément
            if self.editor:
                self.editor.delete_selected_element()
            return
        
        if handled:
            self.move(new_x, new_y)
            self.update_label()
            
            # Mettre à jour les spinboxes de position dans l'éditeur
            if self.editor and hasattr(self.editor, 'prop_x') and hasattr(self.editor, 'prop_y'):
                scale = self.canvas_parent.scale_factor if self.canvas_parent else 1.0
                if scale > 0:
                    self.editor.prop_x.blockSignals(True)
                    self.editor.prop_y.blockSignals(True)
                    self.editor.prop_x.setValue(round(new_x / scale))
                    self.editor.prop_y.setValue(round(new_y / scale))
                    self.editor.prop_x.blockSignals(False)
                    self.editor.prop_y.blockSignals(False)
            
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Sauvegarder l'état après un déplacement au clavier"""
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            if hasattr(self, 'key_move_start_pos') and self.key_move_start_pos is not None:
                if self.pos() != self.key_move_start_pos:
                    if self.editor and hasattr(self.editor, 'save_state'):
                        self.editor.save_state()
                self.key_move_start_pos = None
        super().keyReleaseEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.drag_start_pos = self.pos()  # Sauvegarder position de départ
            
            # Sélectionner l'élément dans l'éditeur
            if self.editor and self.element_data:
                self.editor.select_element(self.element_data, event)
            
            # Sauvegarder l'état AVANT le déplacement
            if self.editor and hasattr(self.editor, 'save_state_before_drag'):
                self.editor.save_state_before_drag()
            
            self.setCursor(Qt.ClosedHandCursor)
            self.setFocus()  # Prendre le focus au clic
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            # Déplacer l'élément
            new_pos = self.mapToParent(event.pos() - self.offset)
            
            # Limiter aux bordures du parent
            parent_rect = self.parent().rect()
            x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
            y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
            
            self.move(x, y)
            self.update_label()  # Mettre à jour les coordonnées et dimensions affichées
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)
            
            # Confirmer la modification si la position a changé
            if hasattr(self, 'drag_start_pos') and self.pos() != self.drag_start_pos:
                if self.editor and hasattr(self.editor, 'confirm_drag_state'):
                    self.editor.confirm_drag_state()
            else:
                # Annuler l'état pré-enregistré si pas de déplacement
                if self.editor and hasattr(self.editor, 'cancel_drag_state'):
                    self.editor.cancel_drag_state()
    
    def mouseDoubleClickEvent(self, event):
        """Ouvrir le dialogue de propriétés au double-clic."""
        if event.button() == Qt.LeftButton and self.editor and self.element_data:
            self.editor.select_element(self.element_data, event)
            self.editor.open_element_properties_dialog(self.element_data)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class TemplateCanvas(QLabel):
    """Canvas pour afficher le template et les éléments déplaçables"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("QLabel { background-color: #E0E0E0; }")
        self.setAlignment(Qt.AlignCenter)
        self.template_pixmap = None
        self.scale_factor = 1.0
        self.original_width = 0
        self.original_height = 0
    
    def set_template(self, image_path):
        """Charger et afficher le template"""
        try:
            # Charger l'image
            if str(image_path).lower().endswith('.psd'):
                from psd_tools import PSDImage
                import tempfile
                import os
                
                # Charger le PSD et le sauvegarder temporairement en PNG
                psd = PSDImage.open(image_path)
                pil_image = psd.composite()
                
                # Stocker la taille originale
                self.original_width = pil_image.width
                self.original_height = pil_image.height
                
                # Sauvegarder dans un fichier temporaire
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
                os.close(temp_fd)
                pil_image.save(temp_path, 'PNG')
                
                # Charger avec QPixmap (plus sûr)
                self.template_pixmap = QPixmap(temp_path)
                
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(temp_path)
                except:
                    pass
            else:
                self.template_pixmap = QPixmap(str(image_path))
                # Stocker la taille originale pour les images normales
                self.original_width = self.template_pixmap.width()
                self.original_height = self.template_pixmap.height()
            
            # Vérifier si le chargement a réussi
            if self.template_pixmap.isNull():
                print(f"Erreur: Pixmap null pour {image_path}")
                return False
            
            # Afficher les dimensions pour debug
            print(f"✅ Template chargé: {self.original_width} x {self.original_height} px")
            
            # Redimensionner pour s'adapter au canvas
            self.update_display()
            return True
        except Exception as e:
            print(f"Erreur chargement template dans éditeur: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_display(self):
        """Mettre à jour l'affichage du template"""
        if self.template_pixmap and self.original_width > 0:
            # Si scale_factor déjà défini, ne pas le recalculer (garde la cohérence)
            if self.scale_factor <= 0:
                # Calculer l'échelle pour s'adapter (basé sur dimensions ORIGINALES)
                available_width = self.width() - 20
                available_height = self.height() - 20
                
                scale_w = available_width / self.original_width
                scale_h = available_height / self.original_height
                self.scale_factor = min(scale_w, scale_h, 1.0)  # Ne pas agrandir
            
            # Calculer les dimensions d'affichage avec le scale_factor (fixe)
            display_width = int(self.original_width * self.scale_factor)
            display_height = int(self.original_height * self.scale_factor)
            
            print(f"📐 Affichage: {display_width}x{display_height} (échelle: {self.scale_factor:.3f})")
            
            # Redimensionner et afficher
            scaled_pixmap = self.template_pixmap.scaled(
                display_width,
                display_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            
            # Ajuster la taille du canvas (fixe, ne change jamais)
            self.setFixedSize(display_width, display_height)
    
    def resizeEvent(self, event):
        """Gérer le redimensionnement"""
        super().resizeEvent(event)
        # Ne pas rappeler update_display() car la taille est fixe


class TemplateEditorDialog(QDialog):
    """Dialogue pour éditer le positionnement des éléments sur le template"""
    
    def __init__(self, template_path=None, config_path=None, parent=None):
        super().__init__(parent)
        self.template_path = None
        self.config_path = None
        self.elements = []
        self.zoom_level = 1.0  # Niveau de zoom par défaut
        
        self.setWindowTitle("Éditeur de Template d'Invitation")
        
        # Activer tous les boutons de la barre de titre (minimize, maximize, close)
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        
        # Utiliser setMinimumSize pour permettre le redimensionnement
        self.setMinimumSize(1200, 700)
        self.resize(1400, 850)  # Taille initiale (laisse de l'espace pour la barre des tâches)
        
        # Toujours initialiser l'UI d'abord
        self.init_ui()
        QTimer.singleShot(0, self.showMaximized)
        
        # Charger le template seulement si fourni et APRÈS que l'UI soit prête
        if template_path:
            self.template_path = template_path
            self.config_path = config_path or Path(template_path).with_suffix('.json')
            # Ne PAS charger automatiquement - éviter les blocages
    
    def init_ui(self):
        """Initialiser l'interface"""
        # Historique pour annuler/rétablir
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 50
        self.is_modified = False  # Suivi des modifications
        
        # Layout principal vertical pour inclure le menu
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === Créer le menu ===
        self.create_menu_bar(main_layout)
        
        # Container pour le contenu
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Appliquer le style moderne
        self.apply_modern_style()
        
        # === Panneau gauche: Canvas ===
        left_panel = QVBoxLayout()
        
        # Canvas avec scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #2c3e50;
            }
        """)
        
        self.canvas = TemplateCanvas()
        self.scroll_area.setWidget(self.canvas)
        
        # Header du canvas
        canvas_header = QLabel("📐 Canvas de Design")
        canvas_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ecf0f1;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
            }
        """)
        left_panel.addWidget(canvas_header)
        
        # Barre de statut du zoom
        self.status_bar = QLabel("Zoom: 100% | Position: - | Élément: Aucun")
        self.status_bar.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #bdc3c7;
                padding: 5px 10px;
                background-color: #2c3e50;
                border-radius: 4px;
            }
        """)
        left_panel.addWidget(self.status_bar)
        
        left_panel.addWidget(self.scroll_area)
        
        # === Panneau droit: Contrôles ===
        right_panel = QVBoxLayout()
        
        # Header des éléments
        elements_header = QLabel("🎨 Éléments")
        elements_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ecf0f1;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
            }
        """)
        right_panel.addWidget(elements_header)
        
        # Groupe: Ajouter des éléments
        add_group = QGroupBox("➕ Ajouter un élément")
        add_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        add_layout = QVBoxLayout()
        
        # Boutons pour ajouter des éléments
        elements_to_add = [
            ("Nom Complet", "text", "nom_complet"),
            ("Titre", "text", "titre"),
            ("Prénom", "text", "prenom"),
            ("Nom", "text", "nom"),
            ("Catégorie", "text", "categorie"),
            ("Nom Événement", "text", "event_nom"),
            ("Date", "text", "event_date"),
            ("Heure", "text", "event_heure"),
            ("Lieu", "text", "event_lieu"),
            ("QR Code", "qr", "qrcode"),
        ]
        
        for label, elem_type, elem_id in elements_to_add:
            btn = QPushButton(f"+ {label}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, l=label, t=elem_type, i=elem_id: 
                              self.add_element(l, t, i))
            add_layout.addWidget(btn)
        
        add_group.setLayout(add_layout)
        right_panel.addWidget(add_group)
        
        # Actions rapides: les propriétés sont maintenant dans un dialogue
        quick_actions_group = QGroupBox("⚙️ Élément sélectionné")
        quick_actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ecf0f1;
                border: 2px solid #06A77D;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        quick_actions_layout = QVBoxLayout()
        
        info_dialog = QLabel("Double-cliquez un élément sur le canvas ou sélectionnez-le puis ouvrez ses propriétés.")
        info_dialog.setWordWrap(True)
        info_dialog.setStyleSheet("color: #bdc3c7; font-size: 12px;")
        quick_actions_layout.addWidget(info_dialog)
        
        btn_open_props = QPushButton("Modifier les propriétés")
        btn_open_props.setStyleSheet("""
            QPushButton {
                background-color: #06A77D;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_open_props.clicked.connect(lambda: self.open_element_properties_dialog(self.selected_element))
        quick_actions_layout.addWidget(btn_open_props)
        
        btn_delete_selected = QPushButton("Supprimer l'élément sélectionné")
        btn_delete_selected.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_delete_selected.clicked.connect(self.delete_selected_element)
        quick_actions_layout.addWidget(btn_delete_selected)
        
        quick_actions_group.setLayout(quick_actions_layout)
        right_panel.addWidget(quick_actions_group)
        
        # Groupe: Propriétés de l'élément sélectionné (avec scroll)
        props_group = QGroupBox("Propriétés")
        props_scroll = QScrollArea()
        props_scroll.setWidgetResizable(True)
        props_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        props_widget = QWidget()
        props_layout = QFormLayout()
        
        # Info sur les dimensions du template
        self.info_template = QLabel("Chargez un template")
        self.info_template.setStyleSheet("color: #666; font-style: italic;")
        self.info_template.setWordWrap(True)
        props_layout.addRow("Template:", self.info_template)
        
        self.prop_x = QSpinBox()
        self.prop_x.setRange(0, 10000)
        self.prop_x.valueChanged.connect(self.update_element_position)
        props_layout.addRow("Position X (px réels):", self.prop_x)
        
        self.prop_y = QSpinBox()
        self.prop_y.setRange(0, 10000)
        self.prop_y.valueChanged.connect(self.update_element_position)
        props_layout.addRow("Position Y (px réels):", self.prop_y)
        
        self.prop_width = QSpinBox()
        self.prop_width.setRange(50, 10000)
        self.prop_width.setValue(300)
        self.prop_width.valueChanged.connect(self.update_element_size)
        props_layout.addRow("Largeur (px réels):", self.prop_width)
        
        self.prop_height = QSpinBox()
        self.prop_height.setRange(20, 10000)
        self.prop_height.setValue(50)
        self.prop_height.valueChanged.connect(self.update_element_size)
        props_layout.addRow("Hauteur (px réels):", self.prop_height)
        
        # Info échelle
        self.info_scale = QLabel("Échelle: 1.0x")
        self.info_scale.setStyleSheet("color: #2E86AB; font-weight: bold;")
        props_layout.addRow("", self.info_scale)
        
        self.prop_font_size = QSpinBox()
        self.prop_font_size.setRange(10, 200)
        self.prop_font_size.setValue(40)
        self.prop_font_size.valueChanged.connect(self.update_element_font_size)
        props_layout.addRow("Taille police:", self.prop_font_size)
        
        # Sélecteur de police
        font_layout = QHBoxLayout()
        self.prop_font_name = QComboBox()
        self.prop_font_name.addItem("Police par défaut", "")
        self.load_available_fonts()
        font_layout.addWidget(self.prop_font_name)
        
        btn_add_font = QPushButton("📁")
        btn_add_font.setToolTip("Ajouter une police personnalisée")
        btn_add_font.setMaximumWidth(40)
        btn_add_font.clicked.connect(self.add_custom_font)
        font_layout.addWidget(btn_add_font)
        props_layout.addRow("Police:", font_layout)
        
        self.prop_color = QPushButton("Choisir couleur")
        self.prop_color.clicked.connect(self.choose_color)
        self.current_color = QColor(0, 0, 0)
        props_layout.addRow("Couleur texte:", self.prop_color)
        
        # Couleurs QR Code
        self.prop_qr_bg_color = QPushButton("Fond QR")
        self.prop_qr_bg_color.clicked.connect(self.choose_qr_bg_color)
        self.current_qr_bg_color = QColor(255, 255, 255)
        self.prop_qr_bg_color.setStyleSheet("background-color: #FFFFFF; color: black;")
        props_layout.addRow("Couleur fond QR:", self.prop_qr_bg_color)
        
        self.prop_qr_fill_color = QPushButton("Éléments QR")
        self.prop_qr_fill_color.clicked.connect(self.choose_qr_fill_color)
        self.current_qr_fill_color = QColor(0, 0, 0)
        self.prop_qr_fill_color.setStyleSheet("background-color: #000000; color: white;")
        props_layout.addRow("Couleur éléments QR:", self.prop_qr_fill_color)
        
        # Bordure QR Code
        self.prop_qr_border_width = QSpinBox()
        self.prop_qr_border_width.setRange(0, 20)
        self.prop_qr_border_width.setValue(0)
        self.prop_qr_border_width.setSuffix(" px")
        self.prop_qr_border_width.valueChanged.connect(self.update_qr_border)
        props_layout.addRow("Bordure QR:", self.prop_qr_border_width)
        
        self.prop_qr_border_color = QPushButton("Couleur bordure")
        self.prop_qr_border_color.clicked.connect(self.choose_qr_border_color)
        self.current_qr_border_color = QColor(0, 0, 0)
        self.prop_qr_border_color.setStyleSheet("background-color: #000000; color: white;")
        props_layout.addRow("Couleur bordure QR:", self.prop_qr_border_color)
        
        # Radius QR Code (coins arrondis)
        self.prop_qr_radius = QSpinBox()
        self.prop_qr_radius.setRange(0, 50)
        self.prop_qr_radius.setValue(0)
        self.prop_qr_radius.setSuffix(" px")
        self.prop_qr_radius.valueChanged.connect(self.update_qr_radius)
        props_layout.addRow("Coins arrondis QR:", self.prop_qr_radius)
        
        # Marge interne QR Code (padding)
        self.prop_qr_padding = QSpinBox()
        self.prop_qr_padding.setRange(0, 50)
        self.prop_qr_padding.setValue(4)
        self.prop_qr_padding.setSuffix(" px")
        self.prop_qr_padding.valueChanged.connect(self.update_qr_padding)
        props_layout.addRow("Marge interne QR:", self.prop_qr_padding)
        
        # Finaliser le scroll des propriétés
        props_widget.setLayout(props_layout)
        props_scroll.setWidget(props_widget)
        
        props_group_layout = QVBoxLayout()
        props_group_layout.addWidget(props_scroll)
        props_group.setLayout(props_group_layout)
        self.props_group = props_group
        self.props_group.hide()
        
        # Liste des éléments
        list_group = QGroupBox("📋 Éléments ajoutés")
        list_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ecf0f1;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        list_layout = QVBoxLayout()
        
        # Scroll area pour la liste
        scroll_list = QScrollArea()
        scroll_list.setWidgetResizable(True)
        scroll_list.setMaximumHeight(200)
        
        self.elements_list_widget = QWidget()
        self.elements_list_layout = QVBoxLayout()
        self.elements_list_widget.setLayout(self.elements_list_layout)
        scroll_list.setWidget(self.elements_list_widget)
        
        list_layout.addWidget(scroll_list)
        
        btn_clear = QPushButton("🗑 Tout supprimer")
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_clear.clicked.connect(self.clear_elements)
        list_layout.addWidget(btn_clear)
        
        list_group.setLayout(list_layout)
        self.list_group = list_group
        self.list_group.hide()
        
        right_panel.addStretch()
        
        # Assembler les panneaux
        content_layout.addLayout(left_panel, 1)
        self.hidden_right_panel = right_panel
        
        main_layout.addWidget(content_widget)
        
        self.setLayout(main_layout)
        
        self.selected_element = None
        
        # Créer les raccourcis clavier
        self.create_shortcuts()
    
    def keyPressEvent(self, event):
        """Gérer les touches directionnelles pour déplacer l'élément sélectionné"""
        if event.matches(QKeySequence.Undo):
            self.undo()
            event.accept()
            return
        if event.matches(QKeySequence.Redo) or (event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier) and event.key() == Qt.Key_Z):
            self.redo()
            event.accept()
            return
        if event.matches(QKeySequence.Save):
            self.save_config()
            event.accept()
            return
        
        if self.selected_element:
            widget = self.selected_element['widget']
            step = 10 if event.modifiers() & Qt.ShiftModifier else 1  # Shift = déplacement rapide
            
            new_x = widget.x()
            new_y = widget.y()
            
            if event.key() == Qt.Key_Left:
                new_x = max(0, widget.x() - step)
            elif event.key() == Qt.Key_Right:
                parent_rect = widget.parent().rect()
                new_x = min(widget.x() + step, parent_rect.width() - widget.width())
            elif event.key() == Qt.Key_Up:
                new_y = max(0, widget.y() - step)
            elif event.key() == Qt.Key_Down:
                parent_rect = widget.parent().rect()
                new_y = min(widget.y() + step, parent_rect.height() - widget.height())
            elif event.key() == Qt.Key_Delete:
                # Supprimer l'élément avec la touche Suppr
                self.delete_selected_element()
                return
            else:
                super().keyPressEvent(event)
                return
            
            widget.move(new_x, new_y)
            widget.update_label()
            
            # Mettre à jour les spinboxes de position
            if hasattr(self, 'prop_x') and hasattr(self, 'prop_y'):
                scale = self.canvas.scale_factor
                if scale > 0:
                    self.prop_x.blockSignals(True)
                    self.prop_y.blockSignals(True)
                    self.prop_x.setValue(round(new_x / scale))
                    self.prop_y.setValue(round(new_y / scale))
                    self.prop_x.blockSignals(False)
                    self.prop_y.blockSignals(False)
        else:
            super().keyPressEvent(event)
    
    def delete_selected_element(self):
        """Supprimer l'élément actuellement sélectionné"""
        if not self.selected_element:
            return
        
        # Sauvegarder l'état avant modification
        self.save_state()
        
        # Trouver et supprimer de la liste
        for i, elem in enumerate(self.elements):
            if elem == self.selected_element:
                elem['widget'].deleteLater()
                self.elements.pop(i)
                break
        
        self.selected_element = None
        self.update_elements_list()
        self.update_status_bar()
    
    def create_menu_bar(self, main_layout):
        """Créer la barre de menu"""
        menu_bar = QMenuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 5px;
                font-size: 13px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 30px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
            QMenu::separator {
                height: 1px;
                background-color: #7f8c8d;
                margin: 5px 10px;
            }
        """)
        
        # === Menu Fichier ===
        file_menu = menu_bar.addMenu("📁 Fichier")
        
        action_save = QAction("💾 Enregistrer", self)
        action_save.triggered.connect(self.save_config)
        file_menu.addAction(action_save)
        
        action_save_as = QAction("💾 Enregistrer sous...", self)
        action_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        action_save_as.setShortcutContext(Qt.WindowShortcut)
        action_save_as.triggered.connect(self.save_config_as)
        file_menu.addAction(action_save_as)
        
        file_menu.addSeparator()
        
        action_load = QAction("📂 Charger template...", self)
        action_load.setShortcut(QKeySequence.Open)
        action_load.setShortcutContext(Qt.WindowShortcut)
        action_load.triggered.connect(self.load_template_dialog)
        file_menu.addAction(action_load)
        
        file_menu.addSeparator()
        
        action_close = QAction("❌ Fermer", self)
        action_close.setShortcut(QKeySequence("Alt+F4"))
        action_close.triggered.connect(self.close)
        file_menu.addAction(action_close)
        
        # === Menu Édition ===
        edit_menu = menu_bar.addMenu("✏️ Édition")
        
        self.action_undo = QAction("↩️ Annuler", self)
        self.action_undo.triggered.connect(self.undo)
        self.action_undo.setEnabled(False)
        edit_menu.addAction(self.action_undo)
        
        self.action_redo = QAction("↪️ Rétablir", self)
        self.action_redo.triggered.connect(self.redo)
        self.action_redo.setEnabled(False)
        edit_menu.addAction(self.action_redo)
        
        edit_menu.addSeparator()
        
        action_delete = QAction("🗑️ Supprimer élément", self)
        action_delete.triggered.connect(self.delete_selected_element)
        edit_menu.addAction(action_delete)
        
        action_clear = QAction("🗑️ Tout supprimer", self)
        action_clear.triggered.connect(self.clear_elements)
        edit_menu.addAction(action_clear)
        
        # === Menu Éléments ===
        elements_menu = menu_bar.addMenu("📋 Éléments")
        
        add_element_menu = elements_menu.addMenu("➕ Ajouter un élément")
        elements_to_add = [
            ("Nom Complet", "text", "nom_complet"),
            ("Titre", "text", "titre"),
            ("Prénom", "text", "prenom"),
            ("Nom", "text", "nom"),
            ("Catégorie", "text", "categorie"),
            ("Nom Événement", "text", "event_nom"),
            ("Date", "text", "event_date"),
            ("Heure", "text", "event_heure"),
            ("Lieu", "text", "event_lieu"),
            ("QR Code", "qr", "qrcode"),
        ]
        for label, elem_type, elem_id in elements_to_add:
            action_add = QAction(label, self)
            action_add.triggered.connect(lambda checked, l=label, t=elem_type, i=elem_id: self.add_element(l, t, i))
            add_element_menu.addAction(action_add)
        
        elements_menu.addSeparator()
        
        action_all_elements = QAction("Afficher tous les éléments...", self)
        action_all_elements.triggered.connect(self.open_elements_dialog)
        elements_menu.addAction(action_all_elements)
        
        elements_menu.addSeparator()
        
        action_selected_properties = QAction("Propriétés de l'élément sélectionné", self)
        action_selected_properties.triggered.connect(lambda: self.open_element_properties_dialog(self.selected_element))
        elements_menu.addAction(action_selected_properties)
        
        action_delete_selected = QAction("Supprimer l'élément sélectionné", self)
        action_delete_selected.triggered.connect(self.delete_selected_element)
        elements_menu.addAction(action_delete_selected)
        
        # === Menu Affichage ===
        view_menu = menu_bar.addMenu("👁️ Affichage")
        
        action_preview = QAction("👁️ Aperçu", self)
        action_preview.setShortcut(QKeySequence("Ctrl+P"))
        action_preview.setShortcutContext(Qt.WindowShortcut)
        action_preview.triggered.connect(self.preview_invitation)
        view_menu.addAction(action_preview)
        
        view_menu.addSeparator()
        
        action_zoom_in = QAction("🔍+ Zoom avant", self)
        action_zoom_in.setShortcut(QKeySequence.ZoomIn)
        action_zoom_in.setShortcutContext(Qt.WindowShortcut)
        action_zoom_in.triggered.connect(self.zoom_in)
        view_menu.addAction(action_zoom_in)
        
        action_zoom_out = QAction("🔍- Zoom arrière", self)
        action_zoom_out.setShortcut(QKeySequence.ZoomOut)
        action_zoom_out.setShortcutContext(Qt.WindowShortcut)
        action_zoom_out.triggered.connect(self.zoom_out)
        view_menu.addAction(action_zoom_out)
        
        action_zoom_reset = QAction("🔄 Réinitialiser zoom", self)
        action_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        action_zoom_reset.setShortcutContext(Qt.WindowShortcut)
        action_zoom_reset.triggered.connect(self.zoom_reset)
        view_menu.addAction(action_zoom_reset)
        
        # === Menu Outils ===
        tools_menu = menu_bar.addMenu("🔧 Outils")
        
        action_generate = QAction("🎨 Génération", self)
        action_generate.setShortcut(QKeySequence("Ctrl+G"))
        action_generate.setShortcutContext(Qt.WindowShortcut)
        action_generate.triggered.connect(self.go_to_generator)
        tools_menu.addAction(action_generate)
        
        tools_menu.addSeparator()
        
        # Sous-menu Zoom
        zoom_submenu = tools_menu.addMenu("🔍 Zoom")
        
        action_zoom_50 = QAction("50%", self)
        action_zoom_50.triggered.connect(lambda: self.set_zoom(0.5))
        zoom_submenu.addAction(action_zoom_50)
        
        action_zoom_75 = QAction("75%", self)
        action_zoom_75.triggered.connect(lambda: self.set_zoom(0.75))
        zoom_submenu.addAction(action_zoom_75)
        
        action_zoom_100 = QAction("100%", self)
        action_zoom_100.triggered.connect(lambda: self.set_zoom(1.0))
        zoom_submenu.addAction(action_zoom_100)
        
        action_zoom_150 = QAction("150%", self)
        action_zoom_150.triggered.connect(lambda: self.set_zoom(1.5))
        zoom_submenu.addAction(action_zoom_150)
        
        action_zoom_200 = QAction("200%", self)
        action_zoom_200.triggered.connect(lambda: self.set_zoom(2.0))
        zoom_submenu.addAction(action_zoom_200)
        
        # === Menu Aide ===
        help_menu = menu_bar.addMenu("❓ Aide")
        
        action_shortcuts = QAction("⌨️ Raccourcis clavier", self)
        action_shortcuts.setShortcut(QKeySequence("F1"))
        action_shortcuts.setShortcutContext(Qt.WindowShortcut)
        action_shortcuts.triggered.connect(self.show_shortcuts_help)
        help_menu.addAction(action_shortcuts)
        
        action_about = QAction("ℹ️ À propos", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)
        
        main_layout.setMenuBar(menu_bar)
    
    def create_shortcuts(self):
        """Créer les raccourcis clavier supplémentaires"""
        # Raccourcis explicites pour undo/redo (plus fiables dans QDialog)
        # IMPORTANT: Stocker comme attributs pour éviter la destruction par le garbage collector
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_undo.setContext(Qt.WindowShortcut)
        self.shortcut_undo.activated.connect(self.undo)
        self.shortcut_undo.activatedAmbiguously.connect(self.undo)
        
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.shortcut_redo.setContext(Qt.WindowShortcut)
        self.shortcut_redo.activated.connect(self.redo)
        self.shortcut_redo.activatedAmbiguously.connect(self.redo)
        
        self.shortcut_redo2 = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.shortcut_redo2.setContext(Qt.WindowShortcut)
        self.shortcut_redo2.activated.connect(self.redo)
        self.shortcut_redo2.activatedAmbiguously.connect(self.redo)
        
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.setContext(Qt.WindowShortcut)
        self.shortcut_save.activated.connect(self.save_config)
        self.shortcut_save.activatedAmbiguously.connect(self.save_config)
        
        self.shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_delete.setContext(Qt.WindowShortcut)
        self.shortcut_delete.activated.connect(self.delete_selected_element)
        self.shortcut_delete.activatedAmbiguously.connect(self.delete_selected_element)
        
        print("✅ Raccourcis clavier initialisés: Ctrl+Z, Ctrl+Y, Ctrl+S, Delete")
    
    def apply_modern_style(self):
        """Appliquer le style moderne à l'application"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a252f;
            }
            QLabel {
                color: #ecf0f1;
            }
            QSpinBox, QComboBox, QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #3498db;
            }
            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QGroupBox {
                font-weight: bold;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
    
    def save_state_before_drag(self):
        """Pré-enregistrer l'état avant un glisser-déposer"""
        self.pending_drag_state = self._capture_current_state()
        print(f"📌 État pré-enregistré avant drag")
    
    def confirm_drag_state(self):
        """Confirmer l'état pré-enregistré après un déplacement effectif"""
        if hasattr(self, 'pending_drag_state') and self.pending_drag_state is not None:
            self.undo_stack.append(self.pending_drag_state)
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            self.pending_drag_state = None
            self.set_modified(True)
            self.update_undo_redo_actions()
            print(f"✅ Drag confirmé - Undo stack: {len(self.undo_stack)}")
    
    def cancel_drag_state(self):
        """Annuler l'état pré-enregistré si pas de déplacement"""
        self.pending_drag_state = None
    
    def _capture_current_state(self):
        """Capturer l'état actuel de tous les éléments"""
        state = []
        for elem in self.elements:
            elem_copy = {
                'id': elem['id'],
                'label': elem['label'],
                'type': elem['type'],
                'x': elem['widget'].x(),
                'y': elem['widget'].y(),
                'width': elem['widget'].width(),
                'height': elem['widget'].height(),
                'font_name': elem.get('font_name', ''),
                'font_size': elem.get('font_size', 40),
                'color': elem.get('color', '#000000'),
                'text_bold': elem.get('text_bold', False),
                'text_italic': elem.get('text_italic', False),
                'text_underline': elem.get('text_underline', False),
                'text_align': elem.get('text_align', 'left'),
            }
            if elem['type'] == 'qr':
                elem_copy['qr_bg_color'] = elem.get('qr_bg_color', '#FFFFFF')
                elem_copy['qr_fill_color'] = elem.get('qr_fill_color', '#000000')
                elem_copy['qr_border_width'] = elem.get('qr_border_width', 0)
                elem_copy['qr_border_color'] = elem.get('qr_border_color', '#000000')
                elem_copy['qr_radius'] = elem.get('qr_radius', 0)
                elem_copy['qr_padding'] = elem.get('qr_padding', 4)
            state.append(elem_copy)
        return state
    
    def save_state(self):
        """Sauvegarder l'état actuel pour annuler/rétablir"""
        state = self._capture_current_state()
        
        self.undo_stack.append(state)
        print(f"💾 État sauvegardé - Stack: {len(self.undo_stack)} états")
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        self.redo_stack.clear()
        self.update_undo_redo_actions()
        
        # Marquer comme modifié
        self.set_modified(True)
    
    def undo(self):
        """Annuler la dernière action"""
        print(f"🔄 Undo demandé - Stack: {len(self.undo_stack)} états")
        if not self.undo_stack:
            print("⚠️ Aucun état à annuler")
            return
        
        # Sauvegarder l'état actuel dans redo
        current_state = self._capture_current_state()
        self.redo_stack.append(current_state)
        
        # Restaurer l'état précédent
        previous_state = self.undo_stack.pop()
        self.restore_state(previous_state)
        self.update_undo_redo_actions()
        print(f"✅ Undo effectué - Undo: {len(self.undo_stack)}, Redo: {len(self.redo_stack)}")
    
    def redo(self):
        """Rétablir la dernière action annulée"""
        print(f"🔄 Redo demandé - Stack: {len(self.redo_stack)} états")
        if not self.redo_stack:
            print("⚠️ Aucun état à rétablir")
            return
        
        # Sauvegarder l'état actuel dans undo
        current_state = self._capture_current_state()
        self.undo_stack.append(current_state)
        
        # Restaurer l'état suivant
        next_state = self.redo_stack.pop()
        self.restore_state(next_state)
        self.update_undo_redo_actions()
        print(f"✅ Redo effectué - Undo: {len(self.undo_stack)}, Redo: {len(self.redo_stack)}")
    
    def restore_state(self, state):
        """Restaurer un état sauvegardé"""
        print(f"🔄 Restauration de {len(state)} éléments...")
        
        # Supprimer tous les éléments actuels
        for elem in self.elements:
            elem['widget'].deleteLater()
        self.elements.clear()
        self.selected_element = None
        
        # Recréer les éléments
        for elem_data in state:
            element = DraggableElement(elem_data['type'], elem_data['label'], self.canvas, editor=self)
            element.move(elem_data['x'], elem_data['y'])
            element.resize(elem_data['width'], elem_data['height'])
            element.show()
            
            new_elem = {
                'widget': element,
                'id': elem_data['id'],
                'label': elem_data['label'],
                'type': elem_data['type'],
                'font_name': elem_data.get('font_name', ''),
                'font_size': elem_data.get('font_size', 40),
                'color': elem_data.get('color', '#000000'),
                'text_bold': elem_data.get('text_bold', False),
                'text_italic': elem_data.get('text_italic', False),
                'text_underline': elem_data.get('text_underline', False),
                'text_align': elem_data.get('text_align', 'left'),
            }
            
            if elem_data['type'] == 'qr':
                new_elem['qr_bg_color'] = elem_data.get('qr_bg_color', '#FFFFFF')
                new_elem['qr_fill_color'] = elem_data.get('qr_fill_color', '#000000')
                new_elem['qr_border_width'] = elem_data.get('qr_border_width', 0)
                new_elem['qr_border_color'] = elem_data.get('qr_border_color', '#000000')
                new_elem['qr_radius'] = elem_data.get('qr_radius', 0)
                new_elem['qr_padding'] = elem_data.get('qr_padding', 4)
            
            # Lier les données à l'élément widget pour la sélection automatique
            element.element_data = new_elem
            
            self.elements.append(new_elem)
            print(f"  ✓ Restauré: {elem_data['label']} à ({elem_data['x']}, {elem_data['y']})")
        
        self.update_elements_list()
        self.update_status_bar()
        print(f"✅ Restauration terminée - {len(self.elements)} éléments")
    
    def update_undo_redo_actions(self):
        """Mettre à jour l'état des actions annuler/rétablir"""
        can_undo = len(self.undo_stack) > 0
        can_redo = len(self.redo_stack) > 0
        
        self.action_undo.setEnabled(can_undo)
        self.action_redo.setEnabled(can_redo)
        
        # Mettre à jour le texte avec le nombre d'actions disponibles
        if can_undo:
            self.action_undo.setText(f"↩️ Annuler ({len(self.undo_stack)})")
        else:
            self.action_undo.setText("↩️ Annuler")
        
        if can_redo:
            self.action_redo.setText(f"↪️ Rétablir ({len(self.redo_stack)})")
        else:
            self.action_redo.setText("↪️ Rétablir")
    
    def set_zoom(self, level):
        """Définir un niveau de zoom spécifique"""
        self.zoom_level = level
        self.apply_zoom()
    
    def save_config_as(self):
        """Enregistrer sous un nouveau nom"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la configuration sous", 
            str(TEMPLATES_DIR), "JSON (*.json)"
        )
        if file_path:
            self.config_path = Path(file_path)
            self.save_config()
    
    def load_template_dialog(self):
        """Ouvrir un dialogue pour charger un template"""
        file_path, _ = SimpleFileSelector.get_open_filename(
            self, "Choisir un template", str(TEMPLATES_DIR), "Images"
        )
        if file_path:
            self.load_template(file_path)
    
    def show_shortcuts_help(self):
        """Afficher l'aide des raccourcis clavier"""
        help_text = """
        <h2>⌨️ Raccourcis clavier</h2>
        <table style='font-size: 12px;'>
        <tr><td><b>Ctrl+S</b></td><td>Enregistrer</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Enregistrer sous</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Ouvrir un template</td></tr>
        <tr><td><b>Ctrl+Z</b></td><td>Annuler</td></tr>
        <tr><td><b>Ctrl+Y</b></td><td>Rétablir</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Aperçu</td></tr>
        <tr><td><b>Ctrl+G</b></td><td>Génération</td></tr>
        <tr><td><b>Ctrl++</b></td><td>Zoom avant</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom arrière</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Réinitialiser zoom</td></tr>
        <tr><td><b>Suppr</b></td><td>Supprimer élément</td></tr>
        <tr><td><b>Flèches</b></td><td>Déplacer élément (1px)</td></tr>
        <tr><td><b>Shift+Flèches</b></td><td>Déplacer élément (10px)</td></tr>
        </table>
        """
        QMessageBox.information(self, "Raccourcis clavier", help_text)
    
    def show_about(self):
        """Afficher la fenêtre À propos"""
        about_text = """
        <h2>📐 Éditeur de Template</h2>
        <p><b>Version 1.0</b></p>
        <p>Éditeur visuel pour positionner les éléments sur les templates d'invitation.</p>
        <hr>
        <p><b>Fonctionnalités:</b></p>
        <ul>
        <li>Positionnement par glisser-déposer</li>
        <li>Déplacement précis au clavier</li>
        <li>Personnalisation des polices et couleurs</li>
        <li>Configuration QR Code avancée</li>
        <li>Annuler / Rétablir illimité</li>
        </ul>
        """
        QMessageBox.about(self, "À propos", about_text)
    
    def set_modified(self, modified=True):
        """Marquer le document comme modifié"""
        self.is_modified = modified
        # Mettre à jour le titre avec un indicateur
        title = "Éditeur de Template"
        if modified:
            title = "* " + title
        self.setWindowTitle(title)
    
    def closeEvent(self, event):
        """Demander confirmation avant de fermer si des modifications non sauvegardées"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Modifications non sauvegardées",
                "Vous avez des modifications non enregistrées.\n\nVoulez-vous les sauvegarder avant de quitter ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:  # Cancel
                event.ignore()
        else:
            event.accept()
    
    def update_status_bar(self):
        """Mettre à jour la barre de statut"""
        zoom_text = f"Zoom: {int(self.zoom_level * 100)}%"
        
        if self.selected_element:
            widget = self.selected_element['widget']
            scale = self.canvas.scale_factor if self.canvas.scale_factor > 0 else 1
            real_x = round(widget.x() / scale)
            real_y = round(widget.y() / scale)
            pos_text = f"Position: ({real_x}, {real_y})"
            elem_text = f"Élément: {self.selected_element['label']}"
        else:
            pos_text = "Position: -"
            elem_text = "Élément: Aucun"
        
        self.status_bar.setText(f"{zoom_text} | {pos_text} | {elem_text}")
    
    def zoom_in(self):
        """Zoom avant (+25%)"""
        self.zoom_level = min(self.zoom_level + 0.25, 3.0)  # Max 300%
        self.apply_zoom()
    
    def zoom_out(self):
        """Zoom arrière (-25%)"""
        self.zoom_level = max(self.zoom_level - 0.25, 0.25)  # Min 25%
        self.apply_zoom()
    
    def zoom_reset(self):
        """Réinitialiser le zoom à 100%"""
        self.zoom_level = 1.0
        self.apply_zoom()
    
    def apply_zoom(self):
        """Appliquer le niveau de zoom au canvas"""
        # Mettre à jour la barre de statut
        self.update_status_bar()
        
        if self.canvas.original_width > 0:
            # Calculer le nouveau scale_factor basé sur le zoom
            # Le scale_factor de base est stocké, on le multiplie par le zoom
            if not hasattr(self.canvas, 'base_scale_factor'):
                self.canvas.base_scale_factor = self.canvas.scale_factor
            
            # Nouveau scale_factor = base * zoom
            old_scale = self.canvas.scale_factor
            self.canvas.scale_factor = self.canvas.base_scale_factor * self.zoom_level
            
            # Recalculer les dimensions d'affichage
            display_width = int(self.canvas.original_width * self.canvas.scale_factor)
            display_height = int(self.canvas.original_height * self.canvas.scale_factor)
            
            # Redimensionner le pixmap
            scaled_pixmap = self.canvas.template_pixmap.scaled(
                display_width,
                display_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.canvas.setPixmap(scaled_pixmap)
            self.canvas.setFixedSize(display_width, display_height)
            
            # Repositionner et redimensionner tous les éléments
            scale_ratio = self.canvas.scale_factor / old_scale
            for elem in self.elements:
                widget = elem['widget']
                new_x = round(widget.x() * scale_ratio)
                new_y = round(widget.y() * scale_ratio)
                new_width = round(widget.width() * scale_ratio)
                new_height = round(widget.height() * scale_ratio)
                
                widget.move(new_x, new_y)
                widget.resize(new_width, new_height)
                widget.update_label()
            
            # Mettre à jour l'affichage de l'échelle
            self.info_scale.setText(f"Échelle: {self.canvas.scale_factor:.3f}x (zoom: {int(self.zoom_level * 100)}%)")
            
            print(f"🔍 Zoom: {int(self.zoom_level * 100)}% (échelle: {self.canvas.scale_factor:.3f})")
    
    def go_to_generator(self):
        """Fermer l'éditeur et diriger vers l'onglet de génération"""
        # Sauvegarder automatiquement la configuration avant de fermer
        if self.template_path and len(self.elements) > 0:
            try:
                self.save_config()
            except:
                pass
        
        # Fermer l'éditeur
        self.accept()
        
        # Diriger vers l'onglet de génération si le parent est la fenêtre principale
        if self.parent() and hasattr(self.parent(), 'tabs'):
            self.parent().tabs.setCurrentIndex(2)  # Index 2 = onglet Générateur
    
    def select_template(self):
        """Sélectionner un fichier template"""
        file_path, _ = SimpleFileSelector.get_open_filename(
            self,
            "Sélectionner un template",
            str(TEMPLATES_DIR),
            "Images"
        )
        
        if file_path:
            self.load_template(file_path)
    
    def load_template(self, template_path):
        """Charger un template"""
        try:
            self.template_path = template_path
            self.config_path = Path(template_path).with_suffix('.json')
            
            print(f"\n🔄 Chargement du template: {template_path}")
            
            if self.canvas.set_template(template_path):
                # Mettre à jour les infos
                self.info_template.setText(f"{self.canvas.original_width} x {self.canvas.original_height} px")
                self.info_scale.setText(f"Échelle: {self.canvas.scale_factor:.3f}x")
                
                print(f"✅ Template chargé avec succès")
                print(f"   Dimensions originales: {self.canvas.original_width} x {self.canvas.original_height} px")
                print(f"   Échelle d'affichage: {self.canvas.scale_factor:.3f}x")
                print(f"   Fichier config: {self.config_path}")
                
                # Charger la config si elle existe
                if self.config_path.exists():
                    print(f"📂 Chargement de la configuration existante...")
                    # Attendre que la fenêtre soit complètement affichée et stable
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(500, self.delayed_load_config)
                
                QMessageBox.information(self, "Succès", 
                                      f"Template chargé !\n\n"
                                      f"Dimensions: {self.canvas.original_width} x {self.canvas.original_height} px\n"
                                      f"Échelle affichage: {self.canvas.scale_factor:.3f}x\n\n"
                                      f"Vous pouvez maintenant ajouter des éléments et les positionner.\n\n"
                                      f"💡 Les coordonnées affichées sont en pixels réels.")
            else:
                QMessageBox.warning(self, "Erreur", 
                                  f"Impossible de charger le template.\nVérifiez le format du fichier.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
            print(f"❌ Erreur load_template: {e}")
            import traceback
            traceback.print_exc()
    
    def add_element(self, label, element_type, element_id):
        """Ajouter un élément sur le canvas"""
        # Sauvegarder l'état avant modification
        self.save_state()
        
        # Créer l'élément déplaçable
        element = DraggableElement(element_type, label, self.canvas, editor=self)
        
        # Position initiale (centre du canvas)
        canvas_center_x = (self.canvas.width() - element.width()) // 2
        canvas_center_y = (self.canvas.height() - element.height()) // 2
        element.move(canvas_center_x, canvas_center_y)
        
        # Debug: afficher position initiale
        if self.canvas.scale_factor > 0:
            real_x = round(canvas_center_x / self.canvas.scale_factor)
            real_y = round(canvas_center_y / self.canvas.scale_factor)
            print(f"➕ Ajout {label}: position écran ({canvas_center_x}, {canvas_center_y}) = réelle ({real_x}, {real_y})")
        
        element.show()
        
        # Stocker les infos de l'élément
        element_data = {
            'widget': element,
            'label': label,
            'type': element_type,
            'id': element_id,
            'font_size': 40,
            'font_name': '',
            'color': '#000000',
            'text_bold': False,
            'text_italic': False,
            'text_underline': False,
            'text_align': 'left',
            'qr_bg_color': '#FFFFFF',
            'qr_fill_color': '#000000',
            'qr_border_width': 0,
            'qr_border_color': '#000000',
            'qr_radius': 0,
            'qr_padding': 4
        }
        
        # Lier les données à l'élément widget pour la sélection automatique
        element.element_data = element_data
        
        self.elements.append(element_data)
        self.update_elements_list()
        self.select_element(element_data)
        self.open_element_properties_dialog(element_data)
    
    def select_element(self, element_data, event=None):
        """Sélectionner un élément"""
        # Désélectionner l'élément précédent
        if self.selected_element and self.selected_element != element_data:
            self.selected_element['widget'].set_selected(False)
        
        self.selected_element = element_data
        
        # Mettre en évidence visuellement
        element_data['widget'].set_selected(True)
        
        # Note: Ne PAS rappeler mousePressEvent ici - éviter la récursion
        # Le drag est géré directement dans DraggableElement.mousePressEvent
        
        # Mettre à jour les propriétés (conversion écran -> réel)
        widget = element_data['widget']
        
        # Bloquer temporairement les signaux pour éviter les boucles
        self.prop_x.blockSignals(True)
        self.prop_y.blockSignals(True)
        self.prop_width.blockSignals(True)
        self.prop_height.blockSignals(True)
        self.prop_font_size.blockSignals(True)
        self.prop_font_name.blockSignals(True)
        
        if self.canvas.scale_factor > 0:
            self.prop_x.setValue(round(widget.x() / self.canvas.scale_factor))
            self.prop_y.setValue(round(widget.y() / self.canvas.scale_factor))
            self.prop_width.setValue(round(widget.width() / self.canvas.scale_factor))
            self.prop_height.setValue(round(widget.height() / self.canvas.scale_factor))
        else:
            self.prop_x.setValue(widget.x())
            self.prop_y.setValue(widget.y())
            self.prop_width.setValue(widget.width())
            self.prop_height.setValue(widget.height())
        
        self.prop_font_size.setValue(element_data.get('font_size', 40))
        
        # Mettre à jour la police sélectionnée
        font_name = element_data.get('font_name', '')
        index = self.prop_font_name.findData(font_name)
        if index >= 0:
            self.prop_font_name.setCurrentIndex(index)
        
        # Mettre à jour la couleur
        color_str = element_data.get('color', '#000000')
        self.current_color = QColor(color_str)
        self.prop_color.setStyleSheet(f"background-color: {color_str}; color: white;")
        
        # Mettre à jour les couleurs QR
        qr_bg_color_str = element_data.get('qr_bg_color', '#FFFFFF')
        self.current_qr_bg_color = QColor(qr_bg_color_str)
        text_color_bg = 'black' if QColor(qr_bg_color_str).lightness() > 128 else 'white'
        self.prop_qr_bg_color.setStyleSheet(f"background-color: {qr_bg_color_str}; color: {text_color_bg};")
        
        qr_fill_color_str = element_data.get('qr_fill_color', '#000000')
        self.current_qr_fill_color = QColor(qr_fill_color_str)
        text_color_fill = 'white' if QColor(qr_fill_color_str).lightness() < 128 else 'black'
        self.prop_qr_fill_color.setStyleSheet(f"background-color: {qr_fill_color_str}; color: {text_color_fill};")
        
        # Mettre à jour les propriétés QR supplémentaires
        self.prop_qr_border_width.blockSignals(True)
        self.prop_qr_border_width.setValue(element_data.get('qr_border_width', 0))
        self.prop_qr_border_width.blockSignals(False)
        
        qr_border_color_str = element_data.get('qr_border_color', '#000000')
        self.current_qr_border_color = QColor(qr_border_color_str)
        text_color_border = 'white' if QColor(qr_border_color_str).lightness() < 128 else 'black'
        self.prop_qr_border_color.setStyleSheet(f"background-color: {qr_border_color_str}; color: {text_color_border};")
        
        self.prop_qr_radius.blockSignals(True)
        self.prop_qr_radius.setValue(element_data.get('qr_radius', 0))
        self.prop_qr_radius.blockSignals(False)
        
        self.prop_qr_padding.blockSignals(True)
        self.prop_qr_padding.setValue(element_data.get('qr_padding', 4))
        self.prop_qr_padding.blockSignals(False)
        
        # Réactiver les signaux
        self.prop_x.blockSignals(False)
        self.prop_y.blockSignals(False)
        self.prop_width.blockSignals(False)
        self.prop_height.blockSignals(False)
        self.prop_font_size.blockSignals(False)
        self.prop_font_name.blockSignals(False)
        
        # Connecter les changements
        try:
            self.prop_font_name.currentIndexChanged.disconnect()
        except:
            pass
        self.prop_font_name.currentIndexChanged.connect(self.update_element_font)
        
        # Mettre à jour la barre de statut
        self.update_status_bar()
        
        print(f"✓ Élément sélectionné: {element_data['label']}")
    
    def open_element_properties_dialog(self, element_data):
        """Ouvrir les propriétés d'un élément dans un dialogue dédié."""
        if not element_data:
            QMessageBox.information(self, "Aucun élément", "Sélectionnez d'abord un élément sur le canvas.")
            return
        
        self.select_element(element_data)
        widget = element_data['widget']
        scale = self.canvas.scale_factor if self.canvas.scale_factor > 0 else 1
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Propriétés - {element_data['label']}")
        dialog.setMinimumWidth(460)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a252f;
            }
            QLabel {
                color: #ecf0f1;
            }
            QSpinBox, QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        
        title = QLabel(f"<h2>{element_data['label']}</h2>")
        title.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title)
        
        form = QFormLayout()
        
        spin_x = QSpinBox()
        spin_x.setRange(0, 10000)
        spin_x.setValue(round(widget.x() / scale))
        form.addRow("Position X (px réels):", spin_x)
        
        spin_y = QSpinBox()
        spin_y.setRange(0, 10000)
        spin_y.setValue(round(widget.y() / scale))
        form.addRow("Position Y (px réels):", spin_y)
        
        spin_width = QSpinBox()
        spin_width.setRange(20, 10000)
        spin_width.setValue(round(widget.width() / scale))
        form.addRow("Largeur (px réels):", spin_width)
        
        spin_height = QSpinBox()
        spin_height.setRange(20, 10000)
        spin_height.setValue(round(widget.height() / scale))
        form.addRow("Hauteur (px réels):", spin_height)
        
        spin_font_size = None
        font_combo = None
        text_color_button = None
        check_bold = None
        check_italic = None
        check_underline = None
        align_combo = None
        text_color = QColor(element_data.get('color', '#000000'))
        
        def style_color_button(button, color):
            text_color_name = 'black' if color.lightness() > 128 else 'white'
            button.setStyleSheet(f"background-color: {color.name()}; color: {text_color_name}; padding: 8px;")
        
        def choose_color(current_color, label):
            selected = QColorDialog.getColor(current_color, dialog, label)
            return selected if selected.isValid() else current_color
        
        if element_data['type'] == 'text':
            spin_font_size = QSpinBox()
            spin_font_size.setRange(10, 200)
            spin_font_size.setValue(element_data.get('font_size', 40))
            form.addRow("Taille police:", spin_font_size)
            
            font_combo = QComboBox()
            for i in range(self.prop_font_name.count()):
                font_combo.addItem(self.prop_font_name.itemText(i), self.prop_font_name.itemData(i))
            font_index = font_combo.findData(element_data.get('font_name', ''))
            if font_index >= 0:
                font_combo.setCurrentIndex(font_index)
            form.addRow("Police:", font_combo)
            
            text_color_button = QPushButton("Choisir couleur")
            style_color_button(text_color_button, text_color)
            
            def update_text_color():
                nonlocal text_color
                text_color = choose_color(text_color, "Couleur du texte")
                style_color_button(text_color_button, text_color)
            
            text_color_button.clicked.connect(update_text_color)
            form.addRow("Couleur texte:", text_color_button)
            
            check_bold = QCheckBox("Gras")
            check_bold.setChecked(element_data.get('text_bold', False))
            check_bold.setStyleSheet("color: #ecf0f1;")
            form.addRow("Style:", check_bold)
            
            check_italic = QCheckBox("Italique")
            check_italic.setChecked(element_data.get('text_italic', False))
            check_italic.setStyleSheet("color: #ecf0f1;")
            form.addRow("", check_italic)
            
            check_underline = QCheckBox("Souligné")
            check_underline.setChecked(element_data.get('text_underline', False))
            check_underline.setStyleSheet("color: #ecf0f1;")
            form.addRow("", check_underline)
            
            align_combo = QComboBox()
            align_combo.addItem("Gauche", "left")
            align_combo.addItem("Centré", "center")
            align_combo.addItem("Droite", "right")
            align_index = align_combo.findData(element_data.get('text_align', 'left'))
            if align_index >= 0:
                align_combo.setCurrentIndex(align_index)
            form.addRow("Alignement:", align_combo)
        
        qr_bg_color = QColor(element_data.get('qr_bg_color', '#FFFFFF'))
        qr_fill_color = QColor(element_data.get('qr_fill_color', '#000000'))
        qr_border_color = QColor(element_data.get('qr_border_color', '#000000'))
        spin_qr_border = None
        spin_qr_radius = None
        spin_qr_padding = None
        
        if element_data['type'] == 'qr':
            qr_bg_button = QPushButton("Fond QR")
            style_color_button(qr_bg_button, qr_bg_color)
            
            def update_qr_bg_color():
                nonlocal qr_bg_color
                qr_bg_color = choose_color(qr_bg_color, "Couleur fond QR")
                style_color_button(qr_bg_button, qr_bg_color)
            
            qr_bg_button.clicked.connect(update_qr_bg_color)
            form.addRow("Couleur fond QR:", qr_bg_button)
            
            qr_fill_button = QPushButton("Éléments QR")
            style_color_button(qr_fill_button, qr_fill_color)
            
            def update_qr_fill_color():
                nonlocal qr_fill_color
                qr_fill_color = choose_color(qr_fill_color, "Couleur éléments QR")
                style_color_button(qr_fill_button, qr_fill_color)
            
            qr_fill_button.clicked.connect(update_qr_fill_color)
            form.addRow("Couleur éléments QR:", qr_fill_button)
            
            spin_qr_border = QSpinBox()
            spin_qr_border.setRange(0, 50)
            spin_qr_border.setSuffix(" px")
            spin_qr_border.setValue(element_data.get('qr_border_width', 0))
            form.addRow("Bordure QR:", spin_qr_border)
            
            qr_border_button = QPushButton("Couleur bordure")
            style_color_button(qr_border_button, qr_border_color)
            
            def update_qr_border_color():
                nonlocal qr_border_color
                qr_border_color = choose_color(qr_border_color, "Couleur bordure QR")
                style_color_button(qr_border_button, qr_border_color)
            
            qr_border_button.clicked.connect(update_qr_border_color)
            form.addRow("Couleur bordure QR:", qr_border_button)
            
            spin_qr_radius = QSpinBox()
            spin_qr_radius.setRange(0, 100)
            spin_qr_radius.setSuffix(" px")
            spin_qr_radius.setValue(element_data.get('qr_radius', 0))
            form.addRow("Coins arrondis QR:", spin_qr_radius)
            
            spin_qr_padding = QSpinBox()
            spin_qr_padding.setRange(0, 100)
            spin_qr_padding.setSuffix(" px")
            spin_qr_padding.setValue(element_data.get('qr_padding', 4))
            form.addRow("Marge interne QR:", spin_qr_padding)
        
        layout.addLayout(form)
        
        buttons_layout = QHBoxLayout()
        btn_delete = QPushButton("Supprimer")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px 18px; font-weight: bold;")
        
        def delete_from_dialog():
            self.selected_element = element_data
            self.delete_selected_element()
            dialog.accept()
        
        btn_delete.clicked.connect(delete_from_dialog)
        buttons_layout.addWidget(btn_delete)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(dialog.reject)
        buttons_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Enregistrer")
        btn_save.setStyleSheet("background-color: #06A77D; color: white; padding: 10px 18px; font-weight: bold;")
        
        def apply_properties():
            self.save_state()
            element_data['widget'].move(round(spin_x.value() * scale), round(spin_y.value() * scale))
            element_data['widget'].resize(
                max(20, round(spin_width.value() * scale)),
                max(20, round(spin_height.value() * scale))
            )
            element_data['widget'].update_label()
            
            if element_data['type'] == 'text':
                element_data['font_size'] = spin_font_size.value()
                element_data['font_name'] = font_combo.currentData() or ''
                element_data['color'] = text_color.name()
                element_data['text_bold'] = check_bold.isChecked()
                element_data['text_italic'] = check_italic.isChecked()
                element_data['text_underline'] = check_underline.isChecked()
                element_data['text_align'] = align_combo.currentData()
            
            if element_data['type'] == 'qr':
                element_data['qr_bg_color'] = qr_bg_color.name()
                element_data['qr_fill_color'] = qr_fill_color.name()
                element_data['qr_border_width'] = spin_qr_border.value()
                element_data['qr_border_color'] = qr_border_color.name()
                element_data['qr_radius'] = spin_qr_radius.value()
                element_data['qr_padding'] = spin_qr_padding.value()
            
            self.select_element(element_data)
            self.update_elements_list()
            self.update_status_bar()
            self.set_modified(True)
            dialog.accept()
        
        btn_save.clicked.connect(apply_properties)
        buttons_layout.addWidget(btn_save)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def open_elements_dialog(self):
        """Afficher tous les éléments du template dans un dialogue."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Tous les éléments")
        dialog.setMinimumSize(650, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a252f;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                padding: 8px 12px;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        title = QLabel("<h2>Éléments du template</h2>")
        title.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title)
        
        if not self.elements:
            empty_label = QLabel("Aucun élément ajouté.")
            empty_label.setStyleSheet("color: #bdc3c7; font-style: italic;")
            layout.addWidget(empty_label)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            content = QWidget()
            elements_layout = QVBoxLayout(content)
            
            for elem in self.elements:
                row = QWidget()
                row.setStyleSheet("""
                    QWidget {
                        background-color: #2c3e50;
                        border-radius: 6px;
                    }
                """)
                row_layout = QHBoxLayout(row)
                
                widget = elem['widget']
                scale = self.canvas.scale_factor if self.canvas.scale_factor > 0 else 1
                info = QLabel(
                    f"<b>{elem['label']}</b> ({elem['type']})<br>"
                    f"ID: {elem['id']} | Position: {round(widget.x() / scale)}, {round(widget.y() / scale)}"
                )
                info.setStyleSheet("color: #ecf0f1; padding: 6px;")
                row_layout.addWidget(info, 1)
                
                btn_select = QPushButton("Sélectionner")
                btn_select.setStyleSheet("background-color: #3498db; color: white;")
                btn_select.clicked.connect(lambda checked, e=elem: self.select_element(e))
                row_layout.addWidget(btn_select)
                
                btn_props = QPushButton("Propriétés")
                btn_props.setStyleSheet("background-color: #06A77D; color: white;")
                btn_props.clicked.connect(lambda checked, e=elem: self.open_element_properties_dialog(e))
                row_layout.addWidget(btn_props)
                
                btn_delete = QPushButton("Supprimer")
                btn_delete.setStyleSheet("background-color: #e74c3c; color: white;")
                
                def delete_elem(checked=False, e=elem):
                    self.select_element(e)
                    self.delete_selected_element()
                    dialog.accept()
                
                btn_delete.clicked.connect(delete_elem)
                row_layout.addWidget(btn_delete)
                
                elements_layout.addWidget(row)
            
            elements_layout.addStretch()
            scroll.setWidget(content)
            layout.addWidget(scroll)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.exec_()
    
    def update_element_font(self):
        """Mettre à jour la police de l'élément sélectionné"""
        if self.selected_element:
            font_path = self.prop_font_name.currentData()
            self.selected_element['font_name'] = font_path if font_path else ''
            print(f"✓ Police changée: {Path(font_path).name if font_path else 'Par défaut'}")
    
    def update_element_font_size(self):
        """Mettre à jour la taille de police de l'élément sélectionné"""
        if self.selected_element:
            self.selected_element['font_size'] = self.prop_font_size.value()
            
            # Pour les éléments texte, ajuster automatiquement la hauteur selon la taille de police
            if self.selected_element['type'] == 'text':
                widget = self.selected_element['widget']
                # Hauteur réelle = taille de police en pixels
                new_height_real = self.prop_font_size.value()
                new_height_screen = round(new_height_real * self.canvas.scale_factor)
                
                # Mettre à jour l'indicateur visuel
                widget.resize(widget.width(), max(20, new_height_screen))
                widget.update_label()
                
                # Mettre à jour le spin de hauteur
                self.prop_height.blockSignals(True)
                self.prop_height.setValue(new_height_real)
                self.prop_height.blockSignals(False)
            
            print(f"✓ Taille police: {self.prop_font_size.value()}px")
    
    def update_element_position(self):
        """Mettre à jour la position de l'élément sélectionné"""
        if self.selected_element:
            widget = self.selected_element['widget']
            # Conversion réel -> écran
            new_x = round(self.prop_x.value() * self.canvas.scale_factor)
            new_y = round(self.prop_y.value() * self.canvas.scale_factor)
            
            # Limiter aux bordures du canvas
            max_x = max(0, self.canvas.width() - widget.width())
            max_y = max(0, self.canvas.height() - widget.height())
            new_x = max(0, min(new_x, max_x))
            new_y = max(0, min(new_y, max_y))
            
            widget.move(new_x, new_y)
            widget.update_label()  # Mettre à jour le label avec la nouvelle position
    
    def update_element_size(self):
        """Mettre à jour la taille de l'élément sélectionné"""
        if self.selected_element:
            widget = self.selected_element['widget']
            # Conversion réel -> écran avec valeurs minimales
            new_width = max(20, round(self.prop_width.value() * self.canvas.scale_factor))
            new_height = max(20, round(self.prop_height.value() * self.canvas.scale_factor))
            
            widget.resize(new_width, new_height)
            widget.update_label()  # Mettre à jour le label avec les nouvelles dimensions
    
    def choose_color(self):
        """Choisir une couleur pour l'élément"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid() and self.selected_element:
            self.save_state()
            self.current_color = color
            self.selected_element['color'] = color.name()
            self.prop_color.setStyleSheet(f"background-color: {color.name()}; color: white;")
            print(f"✓ Couleur changée: {color.name()}")
    
    def choose_qr_bg_color(self):
        """Choisir la couleur de fond du QR code"""
        color = QColorDialog.getColor(self.current_qr_bg_color, self)
        if color.isValid() and self.selected_element:
            self.save_state()
            self.current_qr_bg_color = color
            self.selected_element['qr_bg_color'] = color.name()
            text_color = 'black' if color.lightness() > 128 else 'white'
            self.prop_qr_bg_color.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            print(f"✓ Couleur fond QR: {color.name()}")
    
    def choose_qr_fill_color(self):
        """Choisir la couleur des éléments du QR code"""
        color = QColorDialog.getColor(self.current_qr_fill_color, self)
        if color.isValid() and self.selected_element:
            self.save_state()
            self.current_qr_fill_color = color
            self.selected_element['qr_fill_color'] = color.name()
            text_color = 'white' if color.lightness() < 128 else 'black'
            self.prop_qr_fill_color.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            print(f"✓ Couleur éléments QR: {color.name()}")
    
    def choose_qr_border_color(self):
        """Choisir la couleur de la bordure du QR code"""
        color = QColorDialog.getColor(self.current_qr_border_color, self)
        if color.isValid() and self.selected_element:
            self.save_state()
            self.current_qr_border_color = color
            self.selected_element['qr_border_color'] = color.name()
            text_color = 'white' if color.lightness() < 128 else 'black'
            self.prop_qr_border_color.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            print(f"✓ Couleur bordure QR: {color.name()}")
    
    def update_qr_border(self):
        """Mettre à jour l'épaisseur de bordure du QR code"""
        if self.selected_element:
            self.selected_element['qr_border_width'] = self.prop_qr_border_width.value()
            print(f"✓ Bordure QR: {self.prop_qr_border_width.value()}px")
    
    def update_qr_radius(self):
        """Mettre à jour le radius des coins du QR code"""
        if self.selected_element:
            self.selected_element['qr_radius'] = self.prop_qr_radius.value()
            print(f"✓ Radius QR: {self.prop_qr_radius.value()}px")
    
    def update_qr_padding(self):
        """Mettre à jour la marge interne du QR code"""
        if self.selected_element:
            self.selected_element['qr_padding'] = self.prop_qr_padding.value()
            print(f"✓ Marge interne QR: {self.prop_qr_padding.value()}px")
    
    def load_available_fonts(self):
        """Charger la liste des polices disponibles"""
        # Polices du dossier fonts
        if FONTS_DIR.exists():
            for font_file in FONTS_DIR.glob("*.ttf"):
                self.prop_font_name.addItem(font_file.stem, str(font_file))
            for font_file in FONTS_DIR.glob("*.otf"):
                self.prop_font_name.addItem(font_file.stem, str(font_file))
        
        # Polices système Windows
        if os.name == 'nt':
            windows_fonts = Path("C:/Windows/Fonts")
            if windows_fonts.exists():
                common_fonts = ['arial.ttf', 'times.ttf', 'calibri.ttf', 'comic.ttf', 
                               'Georgia.ttf', 'verdana.ttf', 'tahoma.ttf']
                for font_name in common_fonts:
                    font_path = windows_fonts / font_name
                    if font_path.exists():
                        display_name = font_name.replace('.ttf', '')
                        self.prop_font_name.addItem(display_name, str(font_path))
    
    def add_custom_font(self):
        """Ajouter une police personnalisée"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une police",
            str(FONTS_DIR),
            "Polices (*.ttf *.otf);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            try:
                source = Path(file_path)
                # Copier dans le dossier fonts si ce n'est pas déjà le cas
                if source.parent != FONTS_DIR:
                    import shutil
                    dest = FONTS_DIR / source.name
                    shutil.copy(source, dest)
                    font_path = dest
                else:
                    font_path = source
                
                # Ajouter à la liste
                font_name = font_path.stem
                self.prop_font_name.addItem(font_name, str(font_path))
                self.prop_font_name.setCurrentIndex(self.prop_font_name.count() - 1)
                
                # Mettre à jour l'élément sélectionné
                if self.selected_element:
                    self.selected_element['font_name'] = str(font_path)
                
                QMessageBox.information(self, "Succès", 
                                      f"Police '{font_name}' ajoutée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", 
                                   f"Erreur lors de l'ajout de la police:\n{str(e)}")
    
    def update_elements_list(self):
        """Mettre à jour la liste des éléments"""
        # Vider la liste
        while self.elements_list_layout.count():
            child = self.elements_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not self.elements:
            label = QLabel("Aucun élément")
            label.setStyleSheet("color: #999; font-style: italic; padding: 10px;")
            self.elements_list_layout.addWidget(label)
        else:
            for elem in self.elements:
                # Créer un bouton pour chaque élément
                btn = QPushButton(f"{elem['label']} ({elem['type']})")
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        background-color: white;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                        border-color: #2E86AB;
                    }
                    QPushButton:pressed {
                        background-color: #bbdefb;
                    }
                """)
                btn.clicked.connect(lambda checked, e=elem: self.select_element(e))
                self.elements_list_layout.addWidget(btn)
            
            self.elements_list_layout.addStretch()
    
    def clear_elements(self):
        """Supprimer tous les éléments"""
        if self.elements:  # Ne sauvegarder que s'il y a des éléments
            self.save_state()
        for elem in self.elements:
            elem['widget'].deleteLater()
        self.elements.clear()
        self.update_elements_list()
        self.update_status_bar()
    
    def save_config(self):
        """Sauvegarder la configuration des positions"""
        if not self.template_path:
            QMessageBox.warning(self, "Attention", "Aucun template chargé")
            return
        
        config = {
            'template_path': str(self.template_path),
            'template_width': self.canvas.original_width,
            'template_height': self.canvas.original_height,
            'scale_factor': self.canvas.scale_factor,
            'elements': []
        }
        
        for elem in self.elements:
            widget = elem['widget']
            # Convertir les positions écran en positions réelles
            screen_x = widget.x()
            screen_y = widget.y()
            screen_width = widget.width()
            screen_height = widget.height()
            
            if self.canvas.scale_factor > 0:
                real_x = round(screen_x / self.canvas.scale_factor)
                real_y = round(screen_y / self.canvas.scale_factor)
                real_width = round(screen_width / self.canvas.scale_factor)
                real_height = round(screen_height / self.canvas.scale_factor)
            else:
                real_x = screen_x
                real_y = screen_y
                real_width = screen_width
                real_height = screen_height
            
            print(f"💾 Sauvegarde {elem['label']}: écran({screen_x},{screen_y}) -> réel({real_x},{real_y}) [échelle={self.canvas.scale_factor:.3f}]")
            
            config['elements'].append({
                'id': elem['id'],
                'label': elem['label'],
                'type': elem['type'],
                'x': real_x,
                'y': real_y,
                'width': real_width,
                'height': real_height,
                'font_size': elem.get('font_size', 40),
                'font_name': elem.get('font_name', ''),
                'color': elem.get('color', '#000000'),
                'text_bold': elem.get('text_bold', False),
                'text_italic': elem.get('text_italic', False),
                'text_underline': elem.get('text_underline', False),
                'text_align': elem.get('text_align', 'left'),
                'qr_bg_color': elem.get('qr_bg_color', '#FFFFFF'),
                'qr_fill_color': elem.get('qr_fill_color', '#000000'),
                'qr_border_width': elem.get('qr_border_width', 0),
                'qr_border_color': elem.get('qr_border_color', '#000000'),
                'qr_radius': elem.get('qr_radius', 0),
                'qr_padding': elem.get('qr_padding', 4)
            })
        
        # Sauvegarder dans un fichier JSON avec précision maximale
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, sort_keys=False)
        
        # Marquer comme non modifié après sauvegarde
        self.set_modified(False)
        
        print(f"\n💾 Configuration sauvegardée: {self.config_path}")
        print(f"   Template: {self.canvas.original_width}x{self.canvas.original_height}")
        print(f"   Échelle: {self.canvas.scale_factor:.3f}")
        print(f"   Éléments sauvegardés:")
        for elem in config['elements']:
            print(f"     - {elem['label']}: ({elem['x']}, {elem['y']}) {elem['width']}x{elem['height']}")
        
        self.afficher_message_enregistrement(len(config['elements']))
        QMessageBox.information(self, "Succès", 
                              f"Enregistrement effectué !\n{self.config_path}\n\n"
                              f"{len(config['elements'])} élément(s) enregistré(s)")
    
    def afficher_message_enregistrement(self, nombre_elements):
        """Afficher un message temporaire après sauvegarde."""
        self.status_bar.setText(f"✅ Enregistrement effectué - {nombre_elements} élément(s) sauvegardé(s)")
        QTimer.singleShot(3000, self.update_status_bar)
    
    def delayed_load_config(self):
        """Charger la config après stabilisation du canvas"""
        # Forcer une dernière mise à jour du canvas pour avoir le scale_factor final
        self.canvas.update_display()
        # Attendre que le canvas soit vraiment stable
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, self._final_load_config)
    
    def _final_load_config(self):
        """Chargement final après stabilisation complète"""
        print(f"🔄 Scale factor final avant chargement: {self.canvas.scale_factor:.3f}")
        print(f"🔄 Canvas position: ({self.canvas.x()}, {self.canvas.y()})")
        print(f"🔄 Canvas size: {self.canvas.width()}x{self.canvas.height()}")
        self.load_config()
    
    def load_config(self):
        """Charger une configuration existante"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"\n📂 Chargement config: {self.config_path}")
            print(f"   Template original: {config.get('template_width', 'N/A')}x{config.get('template_height', 'N/A')}")
            print(f"   Template actuel: {self.canvas.original_width}x{self.canvas.original_height}")
            print(f"   Échelle actuelle: {self.canvas.scale_factor:.3f}")
            
            # Vérifier la cohérence des dimensions
            saved_width = config.get('template_width', self.canvas.original_width)
            saved_height = config.get('template_height', self.canvas.original_height)
            
            if saved_width != self.canvas.original_width or saved_height != self.canvas.original_height:
                print(f"⚠️ ATTENTION: Les dimensions du template ont changé!")
                print(f"   Sauvegarde: {saved_width}x{saved_height}")
                print(f"   Actuel: {self.canvas.original_width}x{self.canvas.original_height}")
            
            # Supprimer les éléments existants
            self.clear_elements()
            
            # Recréer les éléments
            for elem_config in config.get('elements', []):
                element = DraggableElement(
                    elem_config['type'], 
                    elem_config['label'], 
                    self.canvas,
                    editor=self
                )
                
                # Les positions sont déjà en pixels réels dans le JSON
                # Il faut juste les convertir en pixels écran avec le scale_factor ACTUEL
                real_x = elem_config['x']
                real_y = elem_config['y']
                real_width = elem_config['width']
                real_height = elem_config['height']
                
                # Conversion réel -> écran avec le scale_factor actuel
                screen_x = round(real_x * self.canvas.scale_factor)
                screen_y = round(real_y * self.canvas.scale_factor)
                screen_width = round(real_width * self.canvas.scale_factor)
                screen_height = round(real_height * self.canvas.scale_factor)
                
                print(f"   📍 {elem_config['label']}:")
                print(f"      Réel: ({real_x},{real_y}) {real_width}x{real_height}")
                print(f"      Écran: ({screen_x},{screen_y}) {screen_width}x{screen_height}")
                
                element.move(screen_x, screen_y)
                element.resize(screen_width, screen_height)
                element.update_label()  # Mettre à jour le label avec position et taille
                
                element.show()
                
                # Stocker
                element_data = {
                    'widget': element,
                    'label': elem_config['label'],
                    'type': elem_config['type'],
                    'id': elem_config['id'],
                    'font_size': elem_config.get('font_size', 40),
                    'font_name': elem_config.get('font_name', ''),
                    'color': elem_config.get('color', '#000000'),
                    'text_bold': elem_config.get('text_bold', False),
                    'text_italic': elem_config.get('text_italic', False),
                    'text_underline': elem_config.get('text_underline', False),
                    'text_align': elem_config.get('text_align', 'left'),
                    'qr_bg_color': elem_config.get('qr_bg_color', '#FFFFFF'),
                    'qr_fill_color': elem_config.get('qr_fill_color', '#000000'),
                    'qr_border_width': elem_config.get('qr_border_width', 0),
                    'qr_border_color': elem_config.get('qr_border_color', '#000000'),
                    'qr_radius': elem_config.get('qr_radius', 0),
                    'qr_padding': elem_config.get('qr_padding', 4)
                }
                
                # Lier les données à l'élément widget pour la sélection automatique
                element.element_data = element_data
                
                self.elements.append(element_data)
            
            self.update_elements_list()
            print(f"✅ {len(self.elements)} élément(s) chargé(s)")
            
        except Exception as e:
            print(f"❌ Erreur chargement config: {e}")
            import traceback
            traceback.print_exc()
    
    def preview_invitation(self):
        """Aperçu de l'invitation avec des données de test - 100% précision"""
        if not self.template_path:
            QMessageBox.warning(self, "Attention", "Aucun template chargé")
            return
        
        try:
            # Sauvegarder temporairement la config actuelle
            config = self.get_config()
            temp_config_path = Path(self.template_path).with_suffix('.json')
            
            # Sauvegarder la config existante si elle existe
            backup_config = None
            if temp_config_path.exists():
                with open(temp_config_path, 'r', encoding='utf-8') as f:
                    backup_config = f.read()
            
            # Écrire la config temporaire
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Utiliser le MÊME générateur que pour la production
            from invitation_generator import InvitationGenerator
            
            generator = InvitationGenerator(self.template_path)
            
            # Données de test
            test_data = {
                'id': 999,
                'nom': 'DUPONT',
                'prenom': 'Jean',
                'titre': 'Mr.',
                'categorie': 'VIP',
                'evenement': {
                    'nom': 'APERÇU TEST',
                    'date': '2025-12-25',
                    'heure': '19:00',
                    'lieu': 'Salle de Réception'
                }
            }
            
            # Générer l'aperçu dans un fichier temporaire
            temp_preview = TEMPLATES_DIR / "temp_preview.jpg"
            invitation_path, _ = generator.creer_invitation(test_data, save_path=temp_preview)
            
            # Restaurer la config originale si elle existait
            if backup_config:
                with open(temp_config_path, 'w', encoding='utf-8') as f:
                    f.write(backup_config)
            
            # Afficher l'aperçu dans une fenêtre
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea
            
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("Aperçu 100% précis - Résultat final")
            preview_dialog.setMinimumSize(900, 700)
            
            layout = QVBoxLayout()
            
            # Info
            info_label = QLabel("✅ Aperçu généré avec le même moteur que la production\n"
                               "Ce que vous voyez est EXACTEMENT le résultat final !")
            info_label.setStyleSheet("background-color: #06A77D; color: white; padding: 10px; font-weight: bold;")
            info_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(info_label)
            
            # Zone scrollable pour l'image
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            image_label = QLabel()
            pixmap = QPixmap(str(temp_preview))
            
            # Redimensionner si trop grand pour l'écran
            if pixmap.width() > 800 or pixmap.height() > 600:
                pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            scroll.setWidget(image_label)
            layout.addWidget(scroll)
            
            # Bouton fermer
            btn_close = QPushButton("Fermer")
            btn_close.clicked.connect(preview_dialog.close)
            layout.addWidget(btn_close)
            
            preview_dialog.setLayout(layout)
            preview_dialog.exec_()
            
            # Nettoyer le fichier temporaire
            if temp_preview.exists():
                temp_preview.unlink()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la prévisualisation:\n{str(e)}")
            print(f"Erreur preview_invitation: {e}")
            import traceback
            traceback.print_exc()
    
    def get_config(self):
        """Obtenir la configuration actuelle"""
        config = {'elements': []}
        
        for elem in self.elements:
            widget = elem['widget']
            config['elements'].append({
                'id': elem['id'],
                'type': elem['type'],
                'x': int(widget.x() / self.canvas.scale_factor),
                'y': int(widget.y() / self.canvas.scale_factor),
                'width': int(widget.width() / self.canvas.scale_factor),
                'height': int(widget.height() / self.canvas.scale_factor),
                'font_size': elem.get('font_size', 40),
                'font_name': elem.get('font_name', ''),
                'color': elem.get('color', '#000000'),
                'text_bold': elem.get('text_bold', False),
                'text_italic': elem.get('text_italic', False),
                'text_underline': elem.get('text_underline', False),
                'text_align': elem.get('text_align', 'left'),
                'qr_bg_color': elem.get('qr_bg_color', '#FFFFFF'),
                'qr_fill_color': elem.get('qr_fill_color', '#000000'),
                'qr_border_width': elem.get('qr_border_width', 0),
                'qr_border_color': elem.get('qr_border_color', '#000000'),
                'qr_radius': elem.get('qr_radius', 0),
                'qr_padding': elem.get('qr_padding', 4)
            })
        
        return config
