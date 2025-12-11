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
from PIL import Image
import json
from pathlib import Path
from config import TEMPLATES_DIR
from simple_file_selector import SimpleFileSelector


class DraggableElement(QLabel):
    """Élément déplaçable sur le canvas (zone de texte ou QR code)"""
    
    def __init__(self, element_type, name, parent=None):
        super().__init__(parent)
        self.element_type = element_type  # 'text' ou 'qr'
        self.name = name
        self.dragging = False
        self.offset = QPoint()
        
        # Style visuel
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(46, 134, 171, 100);
                border: 2px dashed #2E86AB;
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
        """)
        self.setText(name)
        self.setAlignment(Qt.AlignCenter)
        
        # Taille par défaut
        if element_type == 'qr':
            self.resize(200, 200)
        else:
            self.resize(300, 50)
        
        self.setCursor(Qt.OpenHandCursor)
    
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
            
            # Vérifier si le chargement a réussi
            if self.template_pixmap.isNull():
                print(f"Erreur: Pixmap null pour {image_path}")
                return False
            
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
        if self.template_pixmap:
            # Calculer l'échelle pour s'adapter
            available_width = self.width() - 20
            available_height = self.height() - 20
            
            scale_w = available_width / self.template_pixmap.width()
            scale_h = available_height / self.template_pixmap.height()
            self.scale_factor = min(scale_w, scale_h, 1.0)  # Ne pas agrandir
            
            # Redimensionner et afficher
            scaled_pixmap = self.template_pixmap.scaled(
                int(self.template_pixmap.width() * self.scale_factor),
                int(self.template_pixmap.height() * self.scale_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """Gérer le redimensionnement"""
        super().resizeEvent(event)
        self.update_display()


class TemplateEditorDialog(QDialog):
    """Dialogue pour éditer le positionnement des éléments sur le template"""
    
    def __init__(self, template_path=None, config_path=None, parent=None):
        super().__init__(parent)
        self.template_path = None
        self.config_path = None
        self.elements = []
        
        self.setWindowTitle("Éditeur de Template d'Invitation")
        self.setGeometry(100, 100, 1400, 900)
        
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
        left_panel.addWidget(scroll)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        btn_load = QPushButton("📂 Charger Template")
        btn_load.clicked.connect(self.select_template)
        btn_layout.addWidget(btn_load)
        
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
        
        # Groupe: Propriétés de l'élément sélectionné
        props_group = QGroupBox("Propriétés")
        props_layout = QFormLayout()
        
        self.prop_x = QSpinBox()
        self.prop_x.setRange(0, 5000)
        self.prop_x.valueChanged.connect(self.update_element_position)
        props_layout.addRow("Position X:", self.prop_x)
        
        self.prop_y = QSpinBox()
        self.prop_y.setRange(0, 5000)
        self.prop_y.valueChanged.connect(self.update_element_position)
        props_layout.addRow("Position Y:", self.prop_y)
        
        self.prop_width = QSpinBox()
        self.prop_width.setRange(50, 2000)
        self.prop_width.setValue(300)
        self.prop_width.valueChanged.connect(self.update_element_size)
        props_layout.addRow("Largeur:", self.prop_width)
        
        self.prop_height = QSpinBox()
        self.prop_height.setRange(20, 2000)
        self.prop_height.setValue(50)
        self.prop_height.valueChanged.connect(self.update_element_size)
        props_layout.addRow("Hauteur:", self.prop_height)
        
        self.prop_font_size = QSpinBox()
        self.prop_font_size.setRange(10, 200)
        self.prop_font_size.setValue(40)
        props_layout.addRow("Taille police:", self.prop_font_size)
        
        self.prop_color = QPushButton("Choisir couleur")
        self.prop_color.clicked.connect(self.choose_color)
        self.current_color = QColor(0, 0, 0)
        props_layout.addRow("Couleur:", self.prop_color)
        
        props_group.setLayout(props_layout)
        right_panel.addWidget(props_group)
        
        # Liste des éléments
        list_group = QGroupBox("Éléments ajoutés")
        list_layout = QVBoxLayout()
        self.elements_list = QLabel("Aucun élément")
        list_layout.addWidget(self.elements_list)
        
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
            
            if self.canvas.set_template(template_path):
                QMessageBox.information(self, "Succès", 
                                      f"Template chargé !\n\nVous pouvez maintenant ajouter des éléments et les positionner.")
            else:
                QMessageBox.warning(self, "Erreur", 
                                  f"Impossible de charger le template.\nVérifiez le format du fichier.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
            print(f"Erreur load_template: {e}")
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
        
        element.show()
        
        # Stocker les infos de l'élément
        element_data = {
            'widget': element,
            'label': label,
            'type': element_type,
            'id': element_id,
            'font_size': 40,
            'color': '#000000'
        }
        
        self.elements.append(element_data)
        self.update_elements_list()
        
        # Permettre la sélection
        element.mousePressEvent = lambda e, elem=element_data: self.select_element(elem, e)
    
    def select_element(self, element_data, event):
        """Sélectionner un élément"""
        self.selected_element = element_data
        
        # Appeler le handler de drag original
        DraggableElement.mousePressEvent(element_data['widget'], event)
        
        # Mettre à jour les propriétés
        widget = element_data['widget']
        self.prop_x.setValue(int(widget.x() / self.canvas.scale_factor))
        self.prop_y.setValue(int(widget.y() / self.canvas.scale_factor))
        self.prop_width.setValue(int(widget.width() / self.canvas.scale_factor))
        self.prop_height.setValue(int(widget.height() / self.canvas.scale_factor))
        self.prop_font_size.setValue(element_data.get('font_size', 40))
    
    def update_element_position(self):
        """Mettre à jour la position de l'élément sélectionné"""
        if self.selected_element:
            widget = self.selected_element['widget']
            widget.move(
                int(self.prop_x.value() * self.canvas.scale_factor),
                int(self.prop_y.value() * self.canvas.scale_factor)
            )
    
    def update_element_size(self):
        """Mettre à jour la taille de l'élément sélectionné"""
        if self.selected_element:
            widget = self.selected_element['widget']
            widget.resize(
                int(self.prop_width.value() * self.canvas.scale_factor),
                int(self.prop_height.value() * self.canvas.scale_factor)
            )
    
    def choose_color(self):
        """Choisir une couleur pour l'élément"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid() and self.selected_element:
            self.current_color = color
            self.selected_element['color'] = color.name()
    
    def update_elements_list(self):
        """Mettre à jour la liste des éléments"""
        if not self.elements:
            self.elements_list.setText("Aucun élément")
        else:
            text = "\n".join([f"• {e['label']} ({e['type']})" for e in self.elements])
            self.elements_list.setText(text)
    
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
            'elements': []
        }
        
        for elem in self.elements:
            widget = elem['widget']
            # Convertir les positions écran en positions réelles
            config['elements'].append({
                'id': elem['id'],
                'label': elem['label'],
                'type': elem['type'],
                'x': int(widget.x() / self.canvas.scale_factor),
                'y': int(widget.y() / self.canvas.scale_factor),
                'width': int(widget.width() / self.canvas.scale_factor),
                'height': int(widget.height() / self.canvas.scale_factor),
                'font_size': elem.get('font_size', 40),
                'color': elem.get('color', '#000000')
            })
        
        # Sauvegarder dans un fichier JSON
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        QMessageBox.information(self, "Succès", 
                              f"Configuration sauvegardée !\n{self.config_path}")
    
    def load_config(self):
        """Charger une configuration existante"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Supprimer les éléments existants
            self.clear_elements()
            
            # Recréer les éléments
            for elem_config in config.get('elements', []):
                element = DraggableElement(
                    elem_config['type'], 
                    elem_config['label'], 
                    self.canvas
                )
                
                # Appliquer la position et la taille (avec échelle)
                element.move(
                    int(elem_config['x'] * self.canvas.scale_factor),
                    int(elem_config['y'] * self.canvas.scale_factor)
                )
                element.resize(
                    int(elem_config['width'] * self.canvas.scale_factor),
                    int(elem_config['height'] * self.canvas.scale_factor)
                )
                
                element.show()
                
                # Stocker
                element_data = {
                    'widget': element,
                    'label': elem_config['label'],
                    'type': elem_config['type'],
                    'id': elem_config['id'],
                    'font_size': elem_config.get('font_size', 40),
                    'color': elem_config.get('color', '#000000')
                }
                
                self.elements.append(element_data)
                element.mousePressEvent = lambda e, elem=element_data: self.select_element(elem, e)
            
            self.update_elements_list()
            
        except Exception as e:
            print(f"Erreur chargement config: {e}")
    
    def preview_invitation(self):
        """Aperçu de l'invitation avec des données de test"""
        if not self.template_path:
            QMessageBox.warning(self, "Attention", "Aucun template chargé")
            return
        
        QMessageBox.information(self, "Aperçu", 
                              "Fonction d'aperçu à venir !\n\n"
                              "Sauvegardez d'abord votre configuration,\n"
                              "puis utilisez le générateur d'invitations.")
    
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
                'color': elem.get('color', '#000000')
            })
        
        return config
