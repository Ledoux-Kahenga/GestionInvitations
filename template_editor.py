"""
Éditeur visuel de template d'invitation
Permet de positionner les éléments (textes, QR code) sur le template
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QScrollArea, QWidget, QComboBox, QSpinBox,
                            QGroupBox, QFormLayout, QColorDialog, QFileDialog,
                            QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage
from PIL import Image, ImageFont
import json
from pathlib import Path
import os
from config import TEMPLATES_DIR, FONTS_DIR
from simple_file_selector import SimpleFileSelector


class DraggableElement(QLabel):
    """Élément déplaçable sur le canvas (zone de texte ou QR code)"""
    
    def __init__(self, element_type, name, parent=None):
        super().__init__(parent)
        self.element_type = element_type  # 'text' ou 'qr'
        self.name = name
        self.dragging = False
        self.offset = QPoint()
        self.canvas_parent = parent
        
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
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
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
        
        # Charger le template seulement si fourni et APRÈS que l'UI soit prête
        if template_path:
            self.template_path = template_path
            self.config_path = config_path or Path(template_path).with_suffix('.json')
            # Ne PAS charger automatiquement - éviter les blocages
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QHBoxLayout()
        
        # === Panneau gauche: Canvas ===
        left_panel = QVBoxLayout()
        
        # Canvas avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.canvas = TemplateCanvas()
        scroll.setWidget(self.canvas)
        
        left_panel.addWidget(QLabel("<h2>📐 Canvas de Design</h2>"))
        
        # Contrôles de zoom
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        btn_zoom_out = QPushButton("➖")
        btn_zoom_out.setMaximumWidth(40)
        btn_zoom_out.setToolTip("Zoom arrière")
        btn_zoom_out.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(btn_zoom_out)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setMinimumWidth(60)
        self.zoom_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        zoom_layout.addWidget(self.zoom_label)
        
        btn_zoom_in = QPushButton("➕")
        btn_zoom_in.setMaximumWidth(40)
        btn_zoom_in.setToolTip("Zoom avant")
        btn_zoom_in.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(btn_zoom_in)
        
        btn_zoom_reset = QPushButton("🔄")
        btn_zoom_reset.setMaximumWidth(40)
        btn_zoom_reset.setToolTip("Réinitialiser le zoom")
        btn_zoom_reset.clicked.connect(self.zoom_reset)
        zoom_layout.addWidget(btn_zoom_reset)
        
        zoom_layout.addStretch()
        left_panel.addLayout(zoom_layout)
        
        left_panel.addWidget(scroll)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        btn_generate = QPushButton("📂 Générer")
        btn_generate.clicked.connect(self.go_to_generator)
        btn_generate.setStyleSheet("background-color: #06A77D; color: white; padding: 10px; font-weight: bold;")
        btn_layout.addWidget(btn_generate)
        
        btn_save = QPushButton("💾 Sauvegarder Configuration")
        btn_save.clicked.connect(self.save_config)
        btn_layout.addWidget(btn_save)
        
        btn_preview = QPushButton("👁 Aperçu")
        btn_preview.clicked.connect(self.preview_invitation)
        btn_layout.addWidget(btn_preview)
        
        left_panel.addLayout(btn_layout)
        
        # === Panneau droit: Contrôles ===
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("<h2>🎨 Éléments</h2>"))
        
        # Groupe: Ajouter des éléments
        add_group = QGroupBox("Ajouter un élément")
        add_layout = QVBoxLayout()
        
        # Boutons pour ajouter des éléments
        elements_to_add = [
            ("Nom Complet", "text", "nom_complet"),
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
            btn.clicked.connect(lambda checked, l=label, t=elem_type, i=elem_id: 
                              self.add_element(l, t, i))
            add_layout.addWidget(btn)
        
        add_group.setLayout(add_layout)
        right_panel.addWidget(add_group)
        
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
        
        # Finaliser le scroll des propriétés
        props_widget.setLayout(props_layout)
        props_scroll.setWidget(props_widget)
        
        props_group_layout = QVBoxLayout()
        props_group_layout.addWidget(props_scroll)
        props_group.setLayout(props_group_layout)
        right_panel.addWidget(props_group)
        
        # Liste des éléments
        list_group = QGroupBox("Éléments ajoutés")
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
        btn_clear.clicked.connect(self.clear_elements)
        list_layout.addWidget(btn_clear)
        
        list_group.setLayout(list_layout)
        right_panel.addWidget(list_group)
        
        right_panel.addStretch()
        
        # Assembler les panneaux
        layout.addLayout(left_panel, 3)
        layout.addLayout(right_panel, 1)
        
        self.setLayout(layout)
        
        self.selected_element = None
    
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
        self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
        
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
        # Créer l'élément déplaçable
        element = DraggableElement(element_type, label, self.canvas)
        
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
            'qr_bg_color': '#FFFFFF',
            'qr_fill_color': '#000000'
        }
        
        self.elements.append(element_data)
        self.update_elements_list()
        
        # Permettre la sélection
        element.mousePressEvent = lambda e, elem=element_data: self.select_element(elem, e)
    
    def select_element(self, element_data, event=None):
        """Sélectionner un élément"""
        # Désélectionner l'élément précédent
        if self.selected_element:
            self.selected_element['widget'].set_selected(False)
        
        self.selected_element = element_data
        
        # Mettre en évidence visuellement
        element_data['widget'].set_selected(True)
        
        # Appeler le handler de drag original si c'est un clic
        if event:
            DraggableElement.mousePressEvent(element_data['widget'], event)
        
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
        
        print(f"✓ Élément sélectionné: {element_data['label']}")
    
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
            self.current_color = color
            self.selected_element['color'] = color.name()
            self.prop_color.setStyleSheet(f"background-color: {color.name()}; color: white;")
            print(f"✓ Couleur changée: {color.name()}")
    
    def choose_qr_bg_color(self):
        """Choisir la couleur de fond du QR code"""
        color = QColorDialog.getColor(self.current_qr_bg_color, self)
        if color.isValid() and self.selected_element:
            self.current_qr_bg_color = color
            self.selected_element['qr_bg_color'] = color.name()
            text_color = 'black' if color.lightness() > 128 else 'white'
            self.prop_qr_bg_color.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            print(f"✓ Couleur fond QR: {color.name()}")
    
    def choose_qr_fill_color(self):
        """Choisir la couleur des éléments du QR code"""
        color = QColorDialog.getColor(self.current_qr_fill_color, self)
        if color.isValid() and self.selected_element:
            self.current_qr_fill_color = color
            self.selected_element['qr_fill_color'] = color.name()
            text_color = 'white' if color.lightness() < 128 else 'black'
            self.prop_qr_fill_color.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")
            print(f"✓ Couleur éléments QR: {color.name()}")
    
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
        for elem in self.elements:
            elem['widget'].deleteLater()
        self.elements.clear()
        self.update_elements_list()
    
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
                'qr_bg_color': elem.get('qr_bg_color', '#FFFFFF'),
                'qr_fill_color': elem.get('qr_fill_color', '#000000')
            })
        
        # Sauvegarder dans un fichier JSON avec précision maximale
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, sort_keys=False)
        
        print(f"\n💾 Configuration sauvegardée: {self.config_path}")
        print(f"   Template: {self.canvas.original_width}x{self.canvas.original_height}")
        print(f"   Échelle: {self.canvas.scale_factor:.3f}")
        print(f"   Éléments sauvegardés:")
        for elem in config['elements']:
            print(f"     - {elem['label']}: ({elem['x']}, {elem['y']}) {elem['width']}x{elem['height']}")
        
        QMessageBox.information(self, "Succès", 
                              f"Configuration sauvegardée !\n{self.config_path}\n\n"
                              f"{len(config['elements'])} élément(s) enregistré(s)")
    
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
                    self.canvas
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
                    'qr_bg_color': elem_config.get('qr_bg_color', '#FFFFFF'),
                    'qr_fill_color': elem_config.get('qr_fill_color', '#000000')
                }
                
                self.elements.append(element_data)
                element.mousePressEvent = lambda e, elem=element_data: self.select_element(elem, e)
            
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
                'qr_bg_color': elem.get('qr_bg_color', '#FFFFFF'),
                'qr_fill_color': elem.get('qr_fill_color', '#000000')
            })
        
        return config
