"""
Application principale - Gestion des Invitations
Interface moderne avec navigation latérale style Landing Page
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
                            QDateEdit, QTimeEdit, QFileDialog, QMessageBox, QSpinBox,
                            QHeaderView, QFrame, QProgressBar, QTextEdit, QStackedWidget,
                            QGraphicsDropShadowEffect, QScrollArea, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer, QPropertyAnimation, QEasingCurve, QSize, QPointF
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon, QPainter, QBrush, QPen, QLinearGradient, QRadialGradient, QPainterPath
from pathlib import Path
from datetime import datetime
import random
import math

from database_model import InvitationModel
from invitation_generator import InvitationGenerator
from qr_scanner import QRScanner
from template_editor import TemplateEditorDialog
from template_editor_simple import TemplateEditorSimple
from simple_file_selector import SimpleFileSelector
from config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, TEMPLATES_DIR, INVITATIONS_DIR


# Couleurs modernes style Landing Page
COLORS = {
    'primary': '#7C3AED',       # Violet principal
    'primary_dark': '#5B21B6',   # Violet foncé
    'primary_light': '#A78BFA',  # Violet clair
    'secondary': '#06B6D4',      # Cyan
    'background': '#0F172A',     # Fond sombre
    'sidebar': '#1E293B',        # Sidebar
    'card': '#334155',           # Cartes
    'text': '#F8FAFC',           # Texte clair
    'text_muted': '#94A3B8',     # Texte atténué
    'success': '#10B981',        # Vert
    'warning': '#F59E0B',        # Orange
    'danger': '#EF4444',         # Rouge
    'accent': '#EC4899',         # Rose accent
}


class StarryBackground(QWidget):
    """Widget avec fond transparent et étoiles réalistes style ciel nocturne
    
    Dimensions calculées pour la zone d'accueil:
    - Largeur: 1120px (1400 - 280 sidebar)
    - Hauteur: 900px
    
    Couleurs: #ffffff (majoritaire), #ec4899, #237c2d, #8a9df3, #5795de
    """
    
    # Couleurs personnalisées des étoiles (blanc majoritaire)
    STAR_COLORS = [
        (QColor(0xFF, 0xFF, 0xFF), 60),  # Blanc - 60% de chance
        (QColor(0xEC, 0x48, 0x99), 10),  # Rose - 10%
        (QColor(0x23, 0x7C, 0x2D), 10),  # Vert - 10%
        (QColor(0x8A, 0x9D, 0xF3), 10),  # Bleu lavande - 10%
        (QColor(0x57, 0x95, 0xDE), 10),  # Bleu ciel - 10%
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.stars = []
        self.generate_stars(45)  # Moins d'étoiles, bien espacées
        
        # Timer pour animation (scintillement léger)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_stars)
        self.animation_timer.start(80)  # 12.5 FPS (plus doux)
        self.time = 0
    
    def get_random_color(self):
        """Obtenir une couleur aléatoire pondérée (plus de blanches)"""
        total = sum(weight for _, weight in self.STAR_COLORS)
        r = random.randint(0, total - 1)
        cumulative = 0
        for color, weight in self.STAR_COLORS:
            cumulative += weight
            if r < cumulative:
                return color
        return self.STAR_COLORS[0][0]
    
    def generate_stars(self, count):
        """Générer des étoiles espacées avec aspect réaliste"""
        random.seed(42)
        
        # Grille pour espacer les étoiles
        grid_size = int(math.sqrt(count)) + 1
        cell_width = 1.0 / grid_size
        cell_height = 1.0 / grid_size
        
        positions = []
        for i in range(grid_size):
            for j in range(grid_size):
                # Position aléatoire dans chaque cellule
                x = i * cell_width + random.uniform(0.1, 0.9) * cell_width
                y = j * cell_height + random.uniform(0.1, 0.9) * cell_height
                positions.append((x, y))
        
        # Prendre seulement le nombre demandé
        random.shuffle(positions)
        positions = positions[:count]
        
        for x, y in positions:
            self.stars.append({
                'x': x,
                'y': y,
                'size': random.uniform(0.8, 2.5),  # Petites tailles réalistes
                'brightness': random.uniform(0.4, 1.0),
                'twinkle_speed': random.uniform(0.3, 1.5),
                'twinkle_offset': random.uniform(0, 6.28),
                'color': self.get_random_color(),
                'is_shooting': False,
                'blink': random.random() < 0.25,  # 25% des étoiles clignotent
                'blink_speed': random.uniform(3, 6),  # Vitesse de clignotement
            })
        
        # Ajouter 2 étoiles filantes
        for _ in range(2):
            self.stars.append({
                'x': random.uniform(0.1, 0.9),
                'y': random.uniform(0.05, 0.25),
                'size': 1.5,
                'brightness': 0,
                'is_shooting': True,
                'shooting_progress': -random.uniform(50, 300),
                'angle': random.uniform(25, 45),
                'speed': random.uniform(2, 4),
                'color': self.get_random_color(),
            })
    
    def animate_stars(self):
        """Animer les étoiles (scintillement doux)"""
        self.time += 0.08
        self.update()
    
    def paintEvent(self, event):
        """Dessiner les étoiles et la lune croissante"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Dessiner la lune croissante en haut à droite
        self.draw_crescent_moon(painter, width, height)
        
        for star in self.stars:
            if star.get('is_shooting'):
                self.draw_shooting_star(painter, star, width, height)
            else:
                x = star['x'] * width
                y = star['y'] * height
                
                # Scintillement doux
                twinkle = (math.sin(self.time * star['twinkle_speed'] + star['twinkle_offset']) + 1) / 2
                current_brightness = star['brightness'] * (0.7 + 0.3 * twinkle)
                
                # Clignotement pour certaines étoiles (on/off rapide)
                if star.get('blink'):
                    blink_value = math.sin(self.time * star['blink_speed'])
                    if blink_value < -0.3:  # Éteinte ~30% du temps
                        current_brightness *= 0.1
                    elif blink_value > 0.7:  # Très brillante ~15% du temps
                        current_brightness = min(1.0, current_brightness * 1.5)
                
                # Couleur simple
                base_color = star['color']
                color = QColor(
                    base_color.red(),
                    base_color.green(),
                    base_color.blue(),
                    int(255 * current_brightness)
                )
                
                # Taille avec léger scintillement
                size = star['size'] * (0.9 + 0.2 * twinkle)
                
                # Dessiner un simple cercle (pas d'ombre, pas de forme complexe)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QPointF(x, y), size, size)
    
    def draw_shooting_star(self, painter, star, width, height):
        """Étoile filante simple"""
        star['shooting_progress'] += star['speed']
        
        if star['shooting_progress'] < 0:
            return
        
        if star['shooting_progress'] > 120:
            star['shooting_progress'] = -random.uniform(150, 500)
            star['x'] = random.uniform(0.1, 0.9)
            star['y'] = random.uniform(0.05, 0.25)
            star['angle'] = random.uniform(25, 45)
            star['color'] = self.get_random_color()
            return
        
        progress = star['shooting_progress']
        angle_rad = math.radians(star['angle'])
        
        start_x = star['x'] * width + progress * math.cos(angle_rad)
        start_y = star['y'] * height + progress * math.sin(angle_rad)
        
        trail_length = 35
        end_x = start_x - trail_length * math.cos(angle_rad)
        end_y = start_y - trail_length * math.sin(angle_rad)
        
        # Traînée simple
        gradient = QLinearGradient(end_x, end_y, start_x, start_y)
        gradient.setColorAt(0, QColor(255, 255, 255, 0))
        gradient.setColorAt(1, QColor(255, 255, 255, 200))
        
        pen = QPen(QBrush(gradient), 1.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))
        
        # Tête
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(start_x, start_y), 1.5, 1.5)
    
    def draw_crescent_moon(self, painter, width, height):
        """Dessiner une lune croissante en haut à droite"""
        # Position de la lune (coin supérieur droit, le plus possible)
        moon_x = width - 50
        moon_y = 40
        moon_radius = 25  # Taille réduite
        
        # Couleur de la lune (jaune pâle/crème, moins opaque)
        moon_color = QColor(252, 245, 220, 180)  # Crème plus subtil
        
        # Dessiner le cercle principal de la lune
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(moon_color))
        painter.drawEllipse(QPointF(moon_x, moon_y), moon_radius, moon_radius)
        
        # Dessiner un cercle sombre pour créer l'effet croissant
        # Décalé vers la droite pour créer une lune croissante gauche
        shadow_offset = 15  # Ajusté pour la nouvelle taille
        shadow_color = QColor(COLORS['background'])  # Couleur du fond
        painter.setBrush(QBrush(shadow_color))
        painter.drawEllipse(QPointF(moon_x + shadow_offset, moon_y - 3), moon_radius - 3, moon_radius - 3)
        
        # Halo très subtil autour de la lune
        halo_gradient = QRadialGradient(moon_x, moon_y, moon_radius * 1.5)
        halo_gradient.setColorAt(0, QColor(252, 245, 220, 15))
        halo_gradient.setColorAt(0.6, QColor(252, 245, 220, 5))
        halo_gradient.setColorAt(1, QColor(252, 245, 220, 0))
        painter.setBrush(QBrush(halo_gradient))
        painter.drawEllipse(QPointF(moon_x, moon_y), moon_radius * 1.5, moon_radius * 1.5)


class NavButton(QPushButton):
    """Bouton de navigation personnalisé"""
    
    def __init__(self, icon_text, text, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = text
        self.is_active = False
        self.setText(f"{icon_text}  {text}")
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()
    
    def set_active(self, active):
        self.is_active = active
        self.update_style()
    
    def update_style(self):
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS['secondary']}, stop:1 #0891B2);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-family: 'Poppins', sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: left;
                }}
            """)
            self.setFont(QFont("Poppins", 10, QFont.Bold))
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_muted']};
                    border: none;
                    border-radius: 12px;
                    padding: 12px 20px;
                    font-family: 'Poppins', sans-serif;
                    font-size: 14px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['card']};
                    color: {COLORS['text']};
                }}
            """)
            self.setFont(QFont("Poppins", 10))


class StatCard(QFrame):
    """Carte de statistique moderne"""
    
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 16px;
                border: 1px solid {color}40;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icône et titre
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
        header.addWidget(icon_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Valeur
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 12px;
        """)
        layout.addWidget(title_label)
    
    def set_value(self, value):
        self.value_label.setText(str(value))


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application avec design moderne"""
    
    def __init__(self):
        super().__init__()
        self.db = InvitationModel()
        self.db.create_tables()
        
        self.setWindowTitle("🎉 Gestion des Invitations")
        self.setGeometry(100, 100, 1400, 900)
        self.setFixedSize(1400, 900)  # Bloque la taille de la fenêtre
        # Supprime toute possibilité de redimensionnement
        self.setMinimumSize(1400, 900)
        self.setMaximumSize(1400, 900)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar (navigation)
        self.sidebar = self.creer_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Zone de contenu principal
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {COLORS['background']};")
        main_layout.addWidget(self.content_stack)
        
        # Créer les pages
        self.page_accueil = self.creer_page_accueil()
        self.page_evenements = self.creer_page_evenements()
        self.page_invites = self.creer_page_invites()
        self.page_generateur = self.creer_page_generateur()
        self.page_statistiques = self.creer_page_statistiques()
        
        # Ajouter les pages au stack
        self.content_stack.addWidget(self.page_accueil)
        self.content_stack.addWidget(self.page_evenements)
        self.content_stack.addWidget(self.page_invites)
        self.content_stack.addWidget(self.page_generateur)
        self.content_stack.addWidget(self.page_statistiques)
        
        # Afficher la page d'accueil par défaut
        self.naviguer_vers(0)
        
        # Charger les données
        self.rafraichir_evenements()
    
    def creer_sidebar(self):
        """Créer la barre de navigation latérale"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar']};
                border-right: 1px solid {COLORS['card']};
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 25, 20, 30)
        layout.setSpacing(8)

        # ===== LOGO STYLISÉ =====
        logo_container = QFrame()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(2)
        
        # Ligne 1: EVENT avec style découpé
        event_label = QLabel("EVENT")
        event_label.setFont(QFont("Poppins", 22, QFont.Black))
        event_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-family: 'Poppins', sans-serif;
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 6px;
            background: transparent;
        """)
        event_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(event_label)
        
        # Ligne 2: MANAGER avec couleur accent
        manager_label = QLabel("MANAGER")
        manager_label.setFont(QFont("Poppins", 14, QFont.Bold))
        manager_label.setStyleSheet(f"""
            color: {COLORS['primary']};
            font-family: 'Poppins', sans-serif;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 8px;
            background: transparent;
            margin-top: -5px;
        """)
        manager_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(manager_label)
        
        # Ligne décorative
        deco_line = QFrame()
        deco_line.setFixedHeight(2)
        deco_line.setFixedWidth(60)
        deco_line.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.2 {COLORS['primary']}, 
                stop:0.8 {COLORS['accent']}, stop:1 transparent);
            border-radius: 1px;
        """)
        logo_layout.addWidget(deco_line, alignment=Qt.AlignCenter)
        
        # Slogan
        slogan_label = QLabel("Vos événements, simplifiés")
        slogan_label.setFont(QFont("Poppins", 8))
        slogan_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-family: 'Poppins', sans-serif;
            font-size: 9px;
            font-style: italic;
            letter-spacing: 1px;
            margin-top: 4px;
            background: transparent;
        """)
        slogan_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(slogan_label)
        
        layout.addWidget(logo_container)
        
        # Séparateur sous le logo
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {COLORS['card']};")
        layout.addWidget(separator)
        layout.addSpacing(25)

        # Bloc menu - positionné juste après le logo
        menu_block = QVBoxLayout()
        menu_block.setSpacing(6)
        self.nav_buttons = []
        nav_items = [
            ("🏠", "Accueil"),
            ("📅", "Événement"),
            ("👥", "Invités"),
            ("🎨", "Générateurs"),
            ("📊", "Statistique"),
        ]
        for i, (icon, text) in enumerate(nav_items):
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self.naviguer_vers(idx))
            self.nav_buttons.append(btn)
            menu_block.addWidget(btn)
        layout.addLayout(menu_block)

        # Spacer flexible pour pousser la version en bas
        layout.addStretch(1)

        # Section inférieure - Version
        version_label = QLabel("v2.0")
        version_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-family: 'Poppins', sans-serif;
            font-size: 10px;
            padding: 8px 16px;
            background: {COLORS['card']}50;
            border-radius: 12px;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        return sidebar
    
    def naviguer_vers(self, index):
        """Naviguer vers une page"""
        self.content_stack.setCurrentIndex(index)
        
        # Mettre à jour les boutons actifs
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        
        # Rafraîchir les données si nécessaire
        if index == 4:  # Statistiques
            self.rafraichir_statistiques()
    
    def creer_page_accueil(self):
        """Créer la page d'accueil - Présentation
        
        Dimensions de la zone d'accueil:
        - Largeur totale: 1120px (fenêtre 1400 - sidebar 280)
        - Hauteur totale: 900px
        - Marges: gauche 60px, haut 30px, droite 0, bas 0
        - Zone utilisable: 1060 x 870 px
        """
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Ajouter le fond étoilé (dimensions: 1120 x 900 px)
        # Les étoiles seront au-dessus de l'image banner
        self.starry_bg = StarryBackground(page)
        self.starry_bg.setGeometry(0, 0, 1120, 900)
        self.starry_bg.raise_()  # Mettre au-dessus de tous les widgets
        
        # Layout principal horizontal pour la présentation
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(60, 30, 0, 0)
        main_layout.setSpacing(40)
        
        # ===== PARTIE GAUCHE - Texte de présentation =====
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)
        
        left_layout.addStretch(2)
        
        # Badge stylisé
        badge = QLabel("✨ GESTION D'ÉVÉNEMENT")
        badge.setStyleSheet(f"""
            color: #F59E0B;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 3px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary']}30, stop:1 transparent);
            padding: 8px 16px;
            border-radius: 20px;
            border-left: 3px solid #F59E0B;
        """)
        left_layout.addWidget(badge)
        
        left_layout.addSpacing(10)
        
        # Titre principal avec effet visuel
        title_label = QLabel("QR CODE")
        title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 72px;
            font-weight: 900;
            letter-spacing: -1px;
            margin: 0px;
            padding: 0px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        """)
        left_layout.addWidget(title_label)
        
        # Sous-titre stylisé avec gradient
        subtitle_label = QLabel("EVENT MANAGER")
        subtitle_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 28px;
            font-weight: bold;
            margin-top: -5px;
            letter-spacing: 2px;
        """)
        left_layout.addWidget(subtitle_label)
        
        left_layout.addSpacing(25)
        
        # Description avec meilleure lisibilité - Police Poppins
        desc_label = QLabel(
            "Créez et gérez vos événements personnalisés avec des QR codes uniques. "
            "Scannez, validez et suivez la présence de vos invités en temps réel."
        )
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Poppins Medium", 12))
        desc_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-family: 'Poppins Medium', 'Poppins', sans-serif;
            font-size: 16px;
            font-weight: 100;
            line-height: 1.6;
            padding: 15px 20px 15px 0px;
            background: {COLORS['sidebar']}90;
            border-radius: 12px;
            margin-right: 40px;
        """)
        left_layout.addWidget(desc_label)
        
        left_layout.addSpacing(30)
        
        # Fonctionnalités en ligne horizontale compacte avec séparateurs
        features_container = QFrame()
        features_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['card']}80;
                border-radius: 20px;
            }}
        """)
        features_h_layout = QHBoxLayout(features_container)
        features_h_layout.setContentsMargins(25, 15, 25, 15)
        features_h_layout.setSpacing(0)
        
        features = [
            ("📅", "Event"),
            ("💌", "Invitation"),
            ("🎫", "Billet"),
            ("🎟️", "Ticket"),
        ]
        
        for i, (icon, text) in enumerate(features):
            # Conteneur pour chaque feature
            item_layout = QHBoxLayout()
            item_layout.setSpacing(8)
            item_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px; background: transparent;")
            icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            item_layout.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setFont(QFont("Poppins", 10, QFont.Bold))
            text_label.setStyleSheet(f"""
                color: {COLORS['text']};
                font-family: 'Poppins', sans-serif;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            """)
            text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item_layout.addWidget(text_label)
            
            features_h_layout.addLayout(item_layout)
            
            # Ajouter un séparateur sauf pour le dernier élément
            if i < len(features) - 1:
                separator = QLabel("•")
                separator.setStyleSheet(f"""
                    color: {COLORS['primary']};
                    font-size: 16px;
                    padding: 0 15px;
                    background: transparent;
                """)
                separator.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                features_h_layout.addWidget(separator)
        
        left_layout.addWidget(features_container)
        
        left_layout.addStretch(2)
        
        main_layout.addWidget(left_container, stretch=1)
        
        # ===== PARTIE DROITE - Image Banner pleine largeur =====
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Charger l'image banner1.png sans marges
        qr_image_label = QLabel()
        qr_image_label.setContentsMargins(0, 0, 0, 0)
        qr_image_path = Path(__file__).parent / "banner1.png"
        
        if qr_image_path.exists():
            pixmap = QPixmap(str(qr_image_path))
            # Adapter l'image à la taille disponible
            pixmap = pixmap.scaled(890, 890, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            qr_image_label.setPixmap(pixmap)
            qr_image_label.setStyleSheet("""
                QLabel {
                    margin: 0px;
                    padding: 0px;
                    border: none;
                }
            """)
        else:
            # Fallback si l'image n'existe pas
            qr_image_label.setText("📱 Image banner1.png\nnon trouvée")
            qr_image_label.setStyleSheet(f"""
                color: {COLORS['text_muted']}; 
                font-size: 18px;
                padding: 50px;
                border: 2px dashed {COLORS['card']};
                border-radius: 20px;
            """)
            qr_image_label.setAlignment(Qt.AlignCenter)
        
        qr_image_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_layout.addWidget(qr_image_label)
        
        main_layout.addWidget(right_container, stretch=1)
        
        # Variables pour les stats (gardées pour compatibilité)
        self.home_card_events = type('obj', (object,), {'set_value': lambda self, x: None})()
        self.home_card_invites = type('obj', (object,), {'set_value': lambda self, x: None})()
        self.home_card_presents = type('obj', (object,), {'set_value': lambda self, x: None})()
        self.home_card_pending = type('obj', (object,), {'set_value': lambda self, x: None})()
        
        # Connecter le redimensionnement pour le fond étoilé
        def on_resize(event):
            self.starry_bg.setGeometry(0, 0, event.size().width(), event.size().height())
            self.starry_bg.raise_()  # Toujours au-dessus
        page.resizeEvent = on_resize
        
        return page
    
    def creer_bouton_action(self, icon, text, color):
        """Créer un bouton d'action stylisé"""
        btn = QPushButton(f"{icon}\n{text}")
        btn.setFixedSize(160, 100)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 2px solid {color}40;
                border-radius: 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color};
                border-color: {color};
            }}
        """)
        return btn
    
    def creer_page_evenements(self):
        """Créer la page de gestion des événements"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # En-tête avec titre et bouton ajouter
        header_layout = QHBoxLayout()
        
        titre = QLabel("📅 Gestion des Événements")
        titre.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 28px;
            font-weight: bold;
        """)
        header_layout.addWidget(titre)
        
        header_layout.addStretch()
        
        # Bouton pour ouvrir le dialogue d'ajout
        btn_nouveau = QPushButton("➕ Nouvel événement")
        btn_nouveau.setCursor(Qt.PointingHandCursor)
        btn_nouveau.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_nouveau.clicked.connect(self.ouvrir_dialog_evenement)
        header_layout.addWidget(btn_nouveau)
        
        layout.addLayout(header_layout)
        
        # Variable pour stocker l'ID en cours de modification
        self.event_id_en_cours = None
        
        # Barre de filtres
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                padding: 15px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setSpacing(15)
        
        # Icône de recherche
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px;")
        filter_layout.addWidget(search_icon)
        
        # Recherche par nom
        self.filter_nom = QLineEdit()
        self.filter_nom.setPlaceholderText("Rechercher par nom...")
        self.appliquer_style_input(self.filter_nom)
        self.filter_nom.setMinimumWidth(200)
        self.filter_nom.textChanged.connect(self.appliquer_filtres_evenements)
        filter_layout.addWidget(self.filter_nom)
        
        # Séparateur
        sep1 = QFrame()
        sep1.setFixedWidth(1)
        sep1.setStyleSheet(f"background-color: {COLORS['text_muted']}50;")
        filter_layout.addWidget(sep1)
        
        # Filtre par date - De
        date_label = QLabel("Du:")
        date_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        filter_layout.addWidget(date_label)
        
        self.filter_date_debut = QDateEdit()
        self.filter_date_debut.setDate(QDate.currentDate().addMonths(-6))
        self.filter_date_debut.setCalendarPopup(True)
        self.appliquer_style_input(self.filter_date_debut)
        self.filter_date_debut.dateChanged.connect(self.appliquer_filtres_evenements)
        filter_layout.addWidget(self.filter_date_debut)
        
        # Filtre par date - À
        date_label2 = QLabel("Au:")
        date_label2.setStyleSheet(f"color: {COLORS['text_muted']};")
        filter_layout.addWidget(date_label2)
        
        self.filter_date_fin = QDateEdit()
        self.filter_date_fin.setDate(QDate.currentDate().addMonths(12))
        self.filter_date_fin.setCalendarPopup(True)
        self.appliquer_style_input(self.filter_date_fin)
        self.filter_date_fin.dateChanged.connect(self.appliquer_filtres_evenements)
        filter_layout.addWidget(self.filter_date_fin)
        
        # Séparateur
        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet(f"background-color: {COLORS['text_muted']}50;")
        filter_layout.addWidget(sep2)
        
        # Bouton réinitialiser
        btn_reset = QPushButton("↺ Réinitialiser")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['text_muted']}50;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
                color: {COLORS['text']};
            }}
        """)
        btn_reset.clicked.connect(self.reinitialiser_filtres_evenements)
        filter_layout.addWidget(btn_reset)
        
        filter_layout.addStretch()
        layout.addWidget(filter_card)
        
        # Tableau des événements
        self.table_events = QTableWidget()
        self.table_events.setColumnCount(7)
        self.table_events.setHorizontalHeaderLabels([
            "ID", "Nom", "Date", "Heure", "Lieu", "Organisateur", "Template"
        ])
        self.appliquer_style_table(self.table_events)
        self.table_events.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_events.itemSelectionChanged.connect(self.on_event_selected)
        self.table_events.cellClicked.connect(self.on_table_cell_clicked)
        
        # Menu contextuel (clic droit)
        self.table_events.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_events.customContextMenuRequested.connect(self.afficher_menu_evenement)
        
        layout.addWidget(self.table_events)
        
        # Info pour l'utilisateur
        info_label = QLabel("💡 Clic droit sur un événement pour modifier ou supprimer")
        info_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 12px;
            font-style: italic;
        """)
        layout.addWidget(info_label)
        
        return page
    
    def afficher_menu_evenement(self, position):
        """Afficher le menu contextuel pour les événements"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        # Vérifier qu'une ligne est sélectionnée
        selected = self.table_events.selectedItems()
        if not selected:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['primary']};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 10px 30px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['primary']};
            }}
        """)
        
        action_modifier = QAction("✏️ Modifier", self)
        action_modifier.triggered.connect(self.preparer_modification_evenement)
        menu.addAction(action_modifier)
        
        action_supprimer = QAction("🗑️ Supprimer", self)
        action_supprimer.triggered.connect(self.supprimer_evenement)
        menu.addAction(action_supprimer)
        
        menu.exec_(self.table_events.mapToGlobal(position))
    
    def creer_page_invites(self):
        """Créer la page de gestion des invités"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # En-tête
        header = QHBoxLayout()
        titre = QLabel("👥 Gestion des Invités")
        titre.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 28px;
            font-weight: bold;
        """)
        header.addWidget(titre)
        header.addStretch()
        
        # Sélecteur d'événement
        event_label = QLabel("Événement:")
        event_label.setStyleSheet(f"color: {COLORS['text']};")
        header.addWidget(event_label)
        
        self.combo_events = QComboBox()
        self.appliquer_style_input(self.combo_events)
        self.combo_events.setMinimumWidth(250)
        self.combo_events.currentIndexChanged.connect(self.rafraichir_invites)
        header.addWidget(self.combo_events)
        
        # Bouton pour ouvrir le dialogue d'ajout
        btn_nouveau = QPushButton("➕ Nouvel invité")
        btn_nouveau.setCursor(Qt.PointingHandCursor)
        btn_nouveau.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_nouveau.clicked.connect(self.ouvrir_dialog_invite)
        header.addWidget(btn_nouveau)
        
        layout.addLayout(header)
        
        # Barre de filtres
        filter_card = QFrame()
        filter_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                padding: 15px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setSpacing(15)
        
        # Icône de recherche
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px;")
        filter_layout.addWidget(search_icon)
        
        # Recherche par nom
        self.filter_invite_nom = QLineEdit()
        self.filter_invite_nom.setPlaceholderText("Rechercher par nom ou titre...")
        self.appliquer_style_input(self.filter_invite_nom)
        self.filter_invite_nom.setMinimumWidth(200)
        self.filter_invite_nom.textChanged.connect(self.appliquer_filtres_invites)
        filter_layout.addWidget(self.filter_invite_nom)
        
        # Séparateur
        sep1 = QFrame()
        sep1.setFixedWidth(1)
        sep1.setStyleSheet(f"background-color: {COLORS['text_muted']}50;")
        filter_layout.addWidget(sep1)
        
        # Filtre par table
        table_label = QLabel("Table:")
        table_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        filter_layout.addWidget(table_label)
        
        self.filter_invite_table = QComboBox()
        self.filter_invite_table.addItem("Toutes", None)
        self.appliquer_style_input(self.filter_invite_table)
        self.filter_invite_table.currentIndexChanged.connect(self.appliquer_filtres_invites)
        filter_layout.addWidget(self.filter_invite_table)
        
        # Bouton gérer les tables
        btn_gerer_tables = QPushButton("⚙️ Gérer tables")
        btn_gerer_tables.setCursor(Qt.PointingHandCursor)
        btn_gerer_tables.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        btn_gerer_tables.clicked.connect(self.ouvrir_gestion_tables)
        filter_layout.addWidget(btn_gerer_tables)
        
        # Séparateur
        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet(f"background-color: {COLORS['text_muted']}50;")
        filter_layout.addWidget(sep2)
        
        # Filtre par statut
        statut_label = QLabel("Statut:")
        statut_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        filter_layout.addWidget(statut_label)
        
        self.filter_invite_statut = QComboBox()
        self.filter_invite_statut.addItems(["Tous", "invité", "présent"])
        self.appliquer_style_input(self.filter_invite_statut)
        self.filter_invite_statut.currentIndexChanged.connect(self.appliquer_filtres_invites)
        filter_layout.addWidget(self.filter_invite_statut)
        
        # Bouton réinitialiser
        btn_reset = QPushButton("↺ Réinitialiser")
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['text_muted']}50;
                padding: 8px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
                color: {COLORS['text']};
            }}
        """)
        btn_reset.clicked.connect(self.reinitialiser_filtres_invites)
        filter_layout.addWidget(btn_reset)
        
        filter_layout.addStretch()
        layout.addWidget(filter_card)
        
        # Tableau des invités
        self.table_invites = QTableWidget()
        self.table_invites.setColumnCount(9)
        self.table_invites.setHorizontalHeaderLabels([
            "ID", "Nom", "Titre", "Email", "Téléphone", "Table", 
            "Accompagnants", "Statut", "QR Code"
        ])
        self.appliquer_style_table(self.table_invites)
        self.table_invites.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Menu contextuel (clic droit)
        self.table_invites.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_invites.customContextMenuRequested.connect(self.afficher_menu_invite)
        
        layout.addWidget(self.table_invites)
        
        # Info pour l'utilisateur
        info_label = QLabel("💡 Clic droit sur un invité pour modifier ou supprimer")
        info_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 12px;
            font-style: italic;
        """)
        layout.addWidget(info_label)
        
        return page
    
    def afficher_menu_invite(self, position):
        """Afficher le menu contextuel pour les invités"""
        from PyQt5.QtWidgets import QMenu, QAction
        
        selected = self.table_invites.selectedItems()
        if not selected:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['primary']};
                padding: 5px;
            }}
            QMenu::item {{
                padding: 10px 30px;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['primary']};
            }}
        """)
        
        action_modifier = QAction("✏️ Modifier", self)
        action_modifier.triggered.connect(self.modifier_invite)
        menu.addAction(action_modifier)
        
        action_supprimer = QAction("🗑️ Supprimer", self)
        action_supprimer.triggered.connect(self.supprimer_invite)
        menu.addAction(action_supprimer)
        
        menu.exec_(self.table_invites.mapToGlobal(position))
    
    def ouvrir_dialog_invite(self, invite_data=None):
        """Ouvrir le dialogue pour ajouter ou modifier un invité"""
        from PyQt5.QtWidgets import QDialog
        
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner un événement")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Nouvel invité" if not invite_data else "Modifier l'invité")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("👤 " + ("Nouvel invité" if not invite_data else "Modifier l'invité"))
        title.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Titre de l'invité
        titre_label = QLabel("Titre")
        titre_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        layout.addWidget(titre_label)
        self.dialog_invite_titre = QComboBox()
        self.dialog_invite_titre.addItems(["Mr.", "Mme", "Couple", "Chorale", "Groupe"])
        self.dialog_invite_titre.setEditable(True)
        self.appliquer_style_input(self.dialog_invite_titre)
        layout.addWidget(self.dialog_invite_titre)
        
        # Nom
        nom_label = QLabel("Nom")
        nom_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        layout.addWidget(nom_label)
        self.dialog_invite_nom = QLineEdit()
        self.dialog_invite_nom.setPlaceholderText("Nom de famille")
        self.appliquer_style_input(self.dialog_invite_nom)
        layout.addWidget(self.dialog_invite_nom)
        
        # Email et Téléphone
        contact_layout = QHBoxLayout()
        
        email_container = QVBoxLayout()
        email_label = QLabel("Email")
        email_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        email_container.addWidget(email_label)
        self.dialog_invite_email = QLineEdit()
        self.dialog_invite_email.setPlaceholderText("email@exemple.com")
        self.appliquer_style_input(self.dialog_invite_email)
        email_container.addWidget(self.dialog_invite_email)
        contact_layout.addLayout(email_container)
        
        tel_container = QVBoxLayout()
        tel_label = QLabel("Téléphone")
        tel_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        tel_container.addWidget(tel_label)
        self.dialog_invite_tel = QLineEdit()
        self.dialog_invite_tel.setPlaceholderText("+33 6 00 00 00 00")
        self.appliquer_style_input(self.dialog_invite_tel)
        tel_container.addWidget(self.dialog_invite_tel)
        contact_layout.addLayout(tel_container)
        
        layout.addLayout(contact_layout)
        
        # Table et Accompagnants
        table_acc_layout = QHBoxLayout()
        
        table_container = QVBoxLayout()
        table_label = QLabel("Table")
        table_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        table_container.addWidget(table_label)
        self.dialog_invite_table = QComboBox()
        self.dialog_invite_table.addItem("Non assigné", None)
        # Charger les tables de l'événement
        event_id = self.combo_events.currentData()
        tables = self.db.obtenir_tables(event_id)
        for table in tables:
            self.dialog_invite_table.addItem(f"{table['nom']} ({table['nb_personnes'] or 0}/{table['capacite']})", table['id'])
        self.appliquer_style_input(self.dialog_invite_table)
        table_container.addWidget(self.dialog_invite_table)
        table_acc_layout.addLayout(table_container)
        
        acc_container = QVBoxLayout()
        acc_label = QLabel("Accompagnants")
        acc_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        acc_container.addWidget(acc_label)
        self.dialog_invite_accompagnants = QSpinBox()
        self.dialog_invite_accompagnants.setMaximum(999)
        self.appliquer_style_input(self.dialog_invite_accompagnants)
        acc_container.addWidget(self.dialog_invite_accompagnants)
        table_acc_layout.addLayout(acc_container)
        
        layout.addLayout(table_acc_layout)
        self.dialog_invite_table.currentIndexChanged.connect(
            lambda _index: self.mettre_a_jour_limite_accompagnants(invite_data)
        )
        
        # Pré-remplir si modification
        if invite_data:
            self.dialog_invite_titre.setCurrentText(invite_data['titre'] if invite_data['titre'] else 'Mr.')
            self.dialog_invite_nom.setText(invite_data['nom'] if invite_data['nom'] else '')
            self.dialog_invite_email.setText(invite_data['email'] if invite_data['email'] else '')
            self.dialog_invite_tel.setText(invite_data['telephone'] if invite_data['telephone'] else '')
            # Sélectionner la table
            table_index = self.dialog_invite_table.findData(invite_data['table_id'])
            if table_index >= 0:
                self.dialog_invite_table.setCurrentIndex(table_index)
            self.dialog_invite_accompagnants.setValue(invite_data['nombre_accompagnants'] if invite_data['nombre_accompagnants'] else 0)
        
        self.mettre_a_jour_limite_accompagnants(invite_data)
        
        layout.addSpacing(10)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setCursor(Qt.PointingHandCursor)
        btn_annuler.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['text_muted']}50;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
            }}
        """)
        btn_annuler.clicked.connect(dialog.reject)
        buttons_layout.addWidget(btn_annuler)
        
        btn_valider = QPushButton("✓ Enregistrer")
        btn_valider.setCursor(Qt.PointingHandCursor)
        btn_valider.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_valider.clicked.connect(lambda: self.valider_dialog_invite(dialog, invite_data))
        buttons_layout.addWidget(btn_valider)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def mettre_a_jour_limite_accompagnants(self, invite_data=None):
        """Adapter le maximum d'accompagnants selon les places disponibles."""
        if not hasattr(self, 'dialog_invite_accompagnants') or not hasattr(self, 'dialog_invite_table'):
            return
        
        table_id = self.dialog_invite_table.currentData()
        if table_id is None:
            self.dialog_invite_accompagnants.setMaximum(999)
            self.dialog_invite_accompagnants.setToolTip("Aucune limite de table sélectionnée")
            return
        
        invite_id = invite_data['id'] if invite_data and invite_data['id'] else None
        places = self.db.obtenir_places_disponibles_table(table_id, invite_id_exclu=invite_id)
        if not places:
            self.dialog_invite_accompagnants.setMaximum(0)
            self.dialog_invite_accompagnants.setToolTip("Table introuvable")
            return
        
        max_accompagnants = max(0, places['disponibles'] - 1)
        self.dialog_invite_accompagnants.setMaximum(max_accompagnants)
        self.dialog_invite_accompagnants.setToolTip(
            f"{places['disponibles']} place(s) disponible(s) sur la table '{places['nom']}'"
        )
    
    def valider_dialog_invite(self, dialog, invite_data=None):
        """Valider et enregistrer l'invité depuis le dialogue"""
        nom = self.dialog_invite_nom.text().strip()
        prenom = ""
        titre = self.dialog_invite_titre.currentText().strip()
        
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est requis")
            return
        
        email = self.dialog_invite_email.text().strip()
        tel = self.dialog_invite_tel.text().strip()
        table_id = self.dialog_invite_table.currentData()
        accompagnants = self.dialog_invite_accompagnants.value()
        nom_affichage = f"{titre} {nom}".strip()
        
        if invite_data and invite_data['id']:
            # Mode modification
            try:
                success = self.db.modifier_invite(
                    invite_data['id'], nom, prenom, email, tel, accompagnants, table_id,
                    titre=titre
                )
            except ValueError as e:
                QMessageBox.warning(self, "Table complète", str(e))
                return
            
            if success:
                QMessageBox.information(self, "Succès", f"Invité '{nom_affichage}' modifié!")
                dialog.accept()
                self.rafraichir_invites()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la modification")
        else:
            # Mode ajout
            event_id = self.combo_events.currentData()
            try:
                invite_id = self.db.ajouter_invite(
                    event_id, nom, prenom, email, tel,
                    nombre_accompagnants=accompagnants, table_id=table_id,
                    titre=titre
                )
            except ValueError as e:
                QMessageBox.warning(self, "Table complète", str(e))
                return
            
            if invite_id:
                QMessageBox.information(self, "Succès", f"Invité '{nom_affichage}' ajouté!")
                dialog.accept()
                self.rafraichir_invites()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
    
    def modifier_invite(self):
        """Ouvrir le dialogue pour modifier l'invité sélectionné"""
        selected = self.table_invites.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        invite_id = int(self.table_invites.item(row, 0).text())
        
        # Récupérer les données de l'invité
        event_id = self.combo_events.currentData()
        invites = self.db.obtenir_invites(event_id)
        invite = next((i for i in invites if i['id'] == invite_id), None)
        
        if invite:
            self.ouvrir_dialog_invite(invite)
    
    def supprimer_invite(self):
        """Supprimer l'invité sélectionné"""
        selected = self.table_invites.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        invite_id = int(self.table_invites.item(row, 0).text())
        invite_nom = self.table_invites.item(row, 1).text()
        invite_titre = self.table_invites.item(row, 2).text()
        invite_affichage = f"{invite_titre} {invite_nom}".strip()
        
        reponse = QMessageBox.question(
            self, "Confirmation",
            f"Supprimer l'invité '{invite_affichage}' ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            if self.db.supprimer_invite(invite_id):
                QMessageBox.information(self, "Succès", f"Invité supprimé!")
                self.rafraichir_invites()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression")
    
    def appliquer_filtres_invites(self):
        """Appliquer les filtres sur la liste des invités"""
        if not hasattr(self, 'all_invites'):
            return
        
        invites = list(self.all_invites)
        
        # Filtre par nom ou titre
        filtre_nom = self.filter_invite_nom.text().strip().lower()
        if filtre_nom:
            invites = [i for i in invites if filtre_nom in i['nom'].lower() or filtre_nom in (i['titre'] or '').lower()]
        
        # Filtre par table
        filtre_table_id = self.filter_invite_table.currentData()
        if filtre_table_id is not None:
            invites = [i for i in invites if i['table_id'] == filtre_table_id]
        
        # Filtre par statut
        filtre_statut = self.filter_invite_statut.currentText()
        if filtre_statut != "Tous":
            invites = [i for i in invites if i['statut'] == filtre_statut]
        
        # Afficher les invités filtrés
        self.afficher_invites_dans_table(invites)
    
    def reinitialiser_filtres_invites(self):
        """Réinitialiser les filtres des invités"""
        self.filter_invite_nom.clear()
        self.filter_invite_table.setCurrentIndex(0)
        self.filter_invite_statut.setCurrentIndex(0)
        self.appliquer_filtres_invites()
    
    def afficher_invites_dans_table(self, invites):
        """Afficher les invités dans le tableau"""
        self.table_invites.setRowCount(len(invites))
        for i, invite in enumerate(invites):
            self.table_invites.setItem(i, 0, QTableWidgetItem(str(invite['id'])))
            self.table_invites.setItem(i, 1, QTableWidgetItem(invite['nom']))
            self.table_invites.setItem(i, 2, QTableWidgetItem(invite['titre'] or ''))
            self.table_invites.setItem(i, 3, QTableWidgetItem(invite['email'] or ''))
            self.table_invites.setItem(i, 4, QTableWidgetItem(invite['telephone'] or ''))
            self.table_invites.setItem(i, 5, QTableWidgetItem(invite['table_nom'] or 'Non assigné'))
            self.table_invites.setItem(i, 6, QTableWidgetItem(str(invite['nombre_accompagnants'])))
            self.table_invites.setItem(i, 7, QTableWidgetItem(invite['statut']))
            self.table_invites.setItem(i, 8, QTableWidgetItem(invite['qr_code'] or ''))
    
    def creer_page_generateur(self):
        """Créer la page du générateur d'invitations"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Titre
        titre = QLabel("🎨 Générateur d'Invitations")
        titre.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(titre)
        
        # Carte de contrôle
        control_card = QFrame()
        control_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                padding: 20px;
            }}
        """)
        control_layout = QVBoxLayout(control_card)
        
        # Ligne 1: Sélection événement
        row1 = QHBoxLayout()
        event_label = QLabel("Sélectionner l'événement:")
        event_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        row1.addWidget(event_label)
        
        self.combo_events_gen = QComboBox()
        self.appliquer_style_input(self.combo_events_gen)
        self.combo_events_gen.setMinimumWidth(300)
        self.combo_events_gen.currentIndexChanged.connect(self.rafraichir_apercu_template)
        row1.addWidget(self.combo_events_gen)
        
        row1.addStretch()
        control_layout.addLayout(row1)
        
        # Ligne 2: Template et actions
        row2 = QHBoxLayout()
        
        template_label = QLabel("📄 Template:")
        template_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 14px;")
        row2.addWidget(template_label)
        
        self.label_template_actuel = QLabel("Aucun template sélectionné")
        self.label_template_actuel.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
            padding: 8px 15px;
            background-color: {COLORS['sidebar']};
        """)
        self.label_template_actuel.setMinimumWidth(250)
        row2.addWidget(self.label_template_actuel)
        
        btn_changer_template = QPushButton("📁 Changer")
        btn_changer_template.setCursor(Qt.PointingHandCursor)
        btn_changer_template.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        btn_changer_template.clicked.connect(self.changer_template_generateur)
        row2.addWidget(btn_changer_template)
        
        btn_editer_template = QPushButton("✏️ Éditer template")
        btn_editer_template.setCursor(Qt.PointingHandCursor)
        btn_editer_template.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """)
        btn_editer_template.clicked.connect(self.editer_template_generateur)
        row2.addWidget(btn_editer_template)
        
        btn_voir_template = QPushButton("👁️ Aperçu")
        btn_voir_template.setCursor(Qt.PointingHandCursor)
        btn_voir_template.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['text_muted']}50;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
            }}
        """)
        btn_voir_template.clicked.connect(self.voir_template_generateur)
        row2.addWidget(btn_voir_template)
        
        row2.addStretch()
        control_layout.addLayout(row2)
        
        # Ligne 3: Bouton générer
        row3 = QHBoxLayout()
        row3.addStretch()
        
        btn_generer = QPushButton("🎨 Générer toutes les invitations")
        btn_generer.setCursor(Qt.PointingHandCursor)
        btn_generer.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_generer.clicked.connect(self.generer_invitations)
        row3.addWidget(btn_generer)
        
        btn_export_pdf = QPushButton("📄 Exporter PDF")
        btn_export_pdf.setCursor(Qt.PointingHandCursor)
        btn_export_pdf.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        btn_export_pdf.clicked.connect(self.exporter_invitations_pdf)
        row3.addWidget(btn_export_pdf)
        
        row3.addStretch()
        control_layout.addLayout(row3)
        
        layout.addWidget(control_card)
        
        # Barre de progression
        self.progress_gen = QProgressBar()
        self.progress_gen.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['card']};
                border: none;
                height: 20px;
                text-align: center;
                color: {COLORS['text']};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
            }}
        """)
        layout.addWidget(self.progress_gen)
        
        # Zone de log
        log_label = QLabel("📝 Journal de génération")
        log_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 16px; font-weight: bold;")
        layout.addWidget(log_label)
        
        self.log_gen = QTextEdit()
        self.log_gen.setReadOnly(True)
        self.log_gen.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: none;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.log_gen)
        
        return page
    
    def rafraichir_apercu_template(self):
        """Rafraîchir l'affichage du template actuel"""
        if self.combo_events_gen.currentIndex() < 0:
            self.label_template_actuel.setText("Aucun événement sélectionné")
            return
        
        event_id = self.combo_events_gen.currentData()
        event = self.db.obtenir_evenement(event_id)
        
        if event and event['template_path']:
            template_path = Path(event['template_path'])
            if template_path.exists():
                self.label_template_actuel.setText(f"📄 {template_path.name}")
                self.label_template_actuel.setStyleSheet(f"""
                    color: {COLORS['success']};
                    font-size: 13px;
                    padding: 8px 15px;
                    background-color: {COLORS['sidebar']};
                """)
            else:
                self.label_template_actuel.setText("⚠️ Template introuvable")
                self.label_template_actuel.setStyleSheet(f"""
                    color: {COLORS['danger']};
                    font-size: 13px;
                    padding: 8px 15px;
                    background-color: {COLORS['sidebar']};
                """)
        else:
            self.label_template_actuel.setText("Aucun template défini")
            self.label_template_actuel.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 13px;
                padding: 8px 15px;
                background-color: {COLORS['sidebar']};
            """)
    
    def changer_template_generateur(self):
        """Changer le template de l'événement sélectionné"""
        if self.combo_events_gen.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        try:
            fichier, _ = SimpleFileSelector.get_open_filename(
                self, "Choisir un template", str(TEMPLATES_DIR), "Images"
            )
            if fichier:
                event_id = self.combo_events_gen.currentData()
                event = self.db.obtenir_evenement(event_id)
                
                if event:
                    success = self.db.modifier_evenement(
                        event_id, event['nom'], event['date'], event['heure'],
                        event['lieu'], event['organisateur'] or '', 
                        event['description'] or '', fichier
                    )
                    if success:
                        QMessageBox.information(self, "Succès", 
                            f"Template mis à jour !\n\n{Path(fichier).name}")
                        self.rafraichir_apercu_template()
                    else:
                        QMessageBox.critical(self, "Erreur", "Erreur lors de la mise à jour")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
    
    def editer_template_generateur(self):
        """Éditer le template de l'événement sélectionné"""
        if self.combo_events_gen.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events_gen.currentData()
        event = self.db.obtenir_evenement(event_id)
        
        if not event or not event['template_path']:
            QMessageBox.warning(self, "Aucun template", 
                "Cet événement n'a pas de template. Veuillez d'abord en choisir un.")
            return
        
        template_path = Path(event['template_path'])
        if not template_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", 
                f"Le template n'existe plus :\n{template_path}\n\nVeuillez en choisir un nouveau.")
            return
        
        try:
            editor = TemplateEditorDialog(parent=self)
            editor.load_template(str(template_path))
            editor.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
    
    def voir_template_generateur(self):
        """Afficher un aperçu du template"""
        if self.combo_events_gen.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events_gen.currentData()
        event = self.db.obtenir_evenement(event_id)
        
        if not event or not event['template_path']:
            QMessageBox.warning(self, "Aucun template", "Cet événement n'a pas de template.")
            return
        
        template_path = Path(event['template_path'])
        if not template_path.exists():
            QMessageBox.warning(self, "Fichier introuvable", 
                f"Le template n'existe plus :\n{template_path}")
            return
        
        # Créer un dialogue d'aperçu
        from PyQt5.QtWidgets import QDialog, QScrollArea
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Aperçu - {template_path.name}")
        dialog.setMinimumSize(900, 700)
        dialog.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        label = QLabel()
        pixmap = QPixmap(str(template_path))
        
        if pixmap.width() > 1200 or pixmap.height() > 800:
            pixmap = pixmap.scaled(1200, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        
        scroll.setWidget(label)
        layout.addWidget(scroll)
        
        btn_fermer = QPushButton("Fermer")
        btn_fermer.setCursor(Qt.PointingHandCursor)
        btn_fermer.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: none;
                padding: 12px 30px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
            }}
        """)
        btn_fermer.clicked.connect(dialog.close)
        layout.addWidget(btn_fermer)
        
        dialog.exec_()
    
    def creer_page_statistiques(self):
        """Créer la page des statistiques"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # En-tête
        header = QHBoxLayout()
        titre = QLabel("📊 Statistiques")
        titre.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 28px;
            font-weight: bold;
        """)
        header.addWidget(titre)
        header.addStretch()
        
        # Sélecteur d'événement
        event_label = QLabel("Événement:")
        event_label.setStyleSheet(f"color: {COLORS['text']};")
        header.addWidget(event_label)
        
        self.combo_events_stats = QComboBox()
        self.appliquer_style_input(self.combo_events_stats)
        self.combo_events_stats.setMinimumWidth(250)
        self.combo_events_stats.currentIndexChanged.connect(self.rafraichir_statistiques)
        header.addWidget(self.combo_events_stats)
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
        """)
        btn_refresh.clicked.connect(self.rafraichir_statistiques)
        header.addWidget(btn_refresh)
        
        layout.addLayout(header)
        
        # Cartes de statistiques
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.stat_card_invites = StatCard("👥", "Total Invités", "0", COLORS['primary'])
        self.stat_card_personnes = StatCard("👨‍👩‍👧‍👦", "Total Personnes", "0", COLORS['secondary'])
        self.stat_card_presents = StatCard("✅", "Présents", "0", COLORS['success'])
        self.stat_card_taux = StatCard("📈", "Taux Présence", "0%", COLORS['accent'])
        
        cards_layout.addWidget(self.stat_card_invites)
        cards_layout.addWidget(self.stat_card_personnes)
        cards_layout.addWidget(self.stat_card_presents)
        cards_layout.addWidget(self.stat_card_taux)
        cards_layout.addStretch()
        
        layout.addLayout(cards_layout)
        
        # Tableau par table
        table_label = QLabel("📋 Répartition par table")
        table_label.setStyleSheet(f"color: {COLORS['text']}; font-size: 18px; font-weight: bold;")
        layout.addWidget(table_label)
        
        self.table_stats_tables = QTableWidget()
        self.table_stats_tables.setColumnCount(4)
        self.table_stats_tables.setHorizontalHeaderLabels([
            "Table", "Nombre d'invités", "Personnes totales", "Présents"
        ])
        self.appliquer_style_table(self.table_stats_tables)
        layout.addWidget(self.table_stats_tables)
        
        return page
    
    def appliquer_style_input(self, widget):
        """Appliquer le style moderne aux inputs"""
        widget.setStyleSheet(f"""
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['card']};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['primary']};
            }}
        """)
    
    def appliquer_style_table(self, table):
        """Appliquer le style moderne aux tableaux"""
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: none;
                border-radius: 12px;
                gridline-color: {COLORS['background']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['background']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['sidebar']};
                color: {COLORS['text']};
                padding: 12px;
                border: none;
                font-weight: bold;
            }}
            QTableCornerButton::section {{
                background-color: {COLORS['sidebar']};
                border: none;
            }}
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
    
    # ============= ÉVÉNEMENTS =============
    
    def ouvrir_dialog_evenement(self, event_data=None):
        """Ouvrir le dialogue pour ajouter ou modifier un événement"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QTimeEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Nouvel événement" if not event_data else "Modifier l'événement")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre du dialogue
        title = QLabel("📅 " + ("Nouvel événement" if not event_data else "Modifier l'événement"))
        title.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Champs du formulaire
        # Nom
        nom_label = QLabel("Nom de l'événement")
        nom_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        layout.addWidget(nom_label)
        
        self.dialog_event_nom = QLineEdit()
        self.dialog_event_nom.setPlaceholderText("Ex: Conférence annuelle 2025")
        self.appliquer_style_input(self.dialog_event_nom)
        layout.addWidget(self.dialog_event_nom)
        
        # Date et Heure sur la même ligne
        datetime_layout = QHBoxLayout()
        
        date_container = QVBoxLayout()
        date_label = QLabel("Date")
        date_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        date_container.addWidget(date_label)
        self.dialog_event_date = QDateEdit()
        self.dialog_event_date.setDate(QDate.currentDate())
        self.dialog_event_date.setCalendarPopup(True)
        self.appliquer_style_input(self.dialog_event_date)
        date_container.addWidget(self.dialog_event_date)
        datetime_layout.addLayout(date_container)
        
        heure_container = QVBoxLayout()
        heure_label = QLabel("Heure")
        heure_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        heure_container.addWidget(heure_label)
        self.dialog_event_heure = QTimeEdit()
        self.dialog_event_heure.setTime(QTime(19, 0))
        self.appliquer_style_input(self.dialog_event_heure)
        heure_container.addWidget(self.dialog_event_heure)
        datetime_layout.addLayout(heure_container)
        
        layout.addLayout(datetime_layout)
        
        # Lieu
        lieu_label = QLabel("Lieu")
        lieu_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        layout.addWidget(lieu_label)
        
        self.dialog_event_lieu = QLineEdit()
        self.dialog_event_lieu.setPlaceholderText("Ex: Salle de conférence, Paris")
        self.appliquer_style_input(self.dialog_event_lieu)
        layout.addWidget(self.dialog_event_lieu)
        
        # Organisateur
        org_label = QLabel("Organisateur")
        org_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        layout.addWidget(org_label)
        
        self.dialog_event_organisateur = QLineEdit()
        self.dialog_event_organisateur.setPlaceholderText("Ex: Société ABC")
        self.appliquer_style_input(self.dialog_event_organisateur)
        layout.addWidget(self.dialog_event_organisateur)
        
        # Pré-remplir si modification
        if event_data:
            self.dialog_event_nom.setText(event_data['nom'] if event_data['nom'] else '')
            self.dialog_event_date.setDate(QDate.fromString(event_data['date'] if event_data['date'] else '', "yyyy-MM-dd"))
            self.dialog_event_heure.setTime(QTime.fromString(event_data['heure'] if event_data['heure'] else '19:00', "HH:mm"))
            self.dialog_event_lieu.setText(event_data['lieu'] if event_data['lieu'] else '')
            self.dialog_event_organisateur.setText(event_data['organisateur'] if event_data['organisateur'] else '')
        
        layout.addSpacing(10)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setCursor(Qt.PointingHandCursor)
        btn_annuler.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['text_muted']}50;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
            }}
        """)
        btn_annuler.clicked.connect(dialog.reject)
        buttons_layout.addWidget(btn_annuler)
        
        btn_valider = QPushButton("✓ Enregistrer")
        btn_valider.setCursor(Qt.PointingHandCursor)
        btn_valider.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_valider.clicked.connect(lambda: self.valider_dialog_evenement(dialog, event_data))
        buttons_layout.addWidget(btn_valider)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def valider_dialog_evenement(self, dialog, event_data=None):
        """Valider et enregistrer l'événement depuis le dialogue"""
        nom = self.dialog_event_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'événement est requis")
            return
        
        date = self.dialog_event_date.date().toString("yyyy-MM-dd")
        heure = self.dialog_event_heure.time().toString("HH:mm")
        lieu = self.dialog_event_lieu.text().strip()
        organisateur = self.dialog_event_organisateur.text().strip()
        
        if event_data and event_data['id']:
            # Mode modification
            success = self.db.modifier_evenement(
                event_data['id'], nom, date, heure, lieu, organisateur
            )
            if success:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' modifié!")
                dialog.accept()
                self.rafraichir_evenements()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la modification")
        else:
            # Mode ajout
            event_id = self.db.ajouter_evenement(nom, date, heure, lieu, organisateur)
            if event_id:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' ajouté!")
                dialog.accept()
                self.rafraichir_evenements()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
    
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
        
        if self.event_id_en_cours:
            success = self.db.modifier_evenement(
                self.event_id_en_cours, nom, date, heure, lieu, organisateur
            )
            if success:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' modifié!")
                self.event_id_en_cours = None
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la modification")
        else:
            event_id = self.db.ajouter_evenement(nom, date, heure, lieu, organisateur)
            if event_id:
                QMessageBox.information(self, "Succès", f"Événement '{nom}' ajouté!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout")
        
        self.event_nom.clear()
        self.event_lieu.clear()
        self.event_organisateur.clear()
        self.event_id_en_cours = None
        self.rafraichir_evenements()
    
    def preparer_modification_evenement(self):
        """Ouvrir le dialogue pour modifier l'événement sélectionné"""
        selected = self.table_events.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement à modifier")
            return
        
        row = selected[0].row()
        event_id = int(self.table_events.item(row, 0).text())
        
        event = self.db.obtenir_evenement(event_id)
        if not event:
            QMessageBox.critical(self, "Erreur", "Événement introuvable")
            return
        
        # Ouvrir le dialogue avec les données de l'événement
        self.ouvrir_dialog_evenement(event)
    
    def supprimer_evenement(self):
        """Supprimer l'événement sélectionné"""
        selected = self.table_events.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement à supprimer")
            return
        
        row = selected[0].row()
        event_id = int(self.table_events.item(row, 0).text())
        event_nom = self.table_events.item(row, 1).text()
        
        reponse = QMessageBox.question(
            self, "Confirmation", 
            f"Supprimer l'événement '{event_nom}' ?\n\n⚠️ Tous les invités seront supprimés!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            if self.db.supprimer_evenement(event_id):
                QMessageBox.information(self, "Succès", f"Événement '{event_nom}' supprimé!")
                self.rafraichir_evenements()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression")
    
    def on_table_cell_clicked(self, row, column):
        """Gérer le clic sur une cellule du tableau"""
        if column == 6:
            event_id = int(self.table_events.item(row, 0).text())
            event_nom = self.table_events.item(row, 1).text()
            
            dialog = QMessageBox(self)
            dialog.setWindowTitle(f"Template - {event_nom}")
            dialog.setText("Choisissez une action pour le template")
            dialog.addButton("📁 Changer", QMessageBox.ActionRole)
            dialog.addButton("Annuler", QMessageBox.RejectRole)
            
            result = dialog.exec_()
            if result == 0:
                self.changer_template_evenement(event_id)
    
    def changer_template_evenement(self, event_id):
        """Changer le template d'un événement"""
        try:
            fichier, _ = SimpleFileSelector.get_open_filename(
                self, "Choisir un template", str(TEMPLATES_DIR), "Images"
            )
            if fichier:
                event = self.db.obtenir_evenement(event_id)
                if event:
                    success = self.db.modifier_evenement(
                        event_id, event['nom'], event['date'], event['heure'],
                        event['lieu'], event['organisateur'] or '', template_path=fichier
                    )
                    if success:
                        QMessageBox.information(self, "Succès", "Template mis à jour!")
                        self.rafraichir_evenements()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def on_event_selected(self):
        """Quand un événement est sélectionné"""
        selected = self.table_events.selectedItems()
        if selected:
            row = selected[0].row()
            event_id = int(self.table_events.item(row, 0).text())
            index = self.combo_events.findData(event_id)
            if index >= 0:
                self.combo_events.setCurrentIndex(index)
    
    def rafraichir_evenements(self):
        """Rafraîchir la liste des événements"""
        events = self.db.obtenir_evenements()
        
        # Stocker tous les événements pour le filtrage
        self.all_events = events
        
        # Appliquer les filtres
        self.appliquer_filtres_evenements()
        
        # Mettre à jour les combos
        self.combo_events.clear()
        self.combo_events_gen.clear()
        self.combo_events_stats.clear()
        
        for event in events:
            text = f"{event['nom']} - {event['date']}"
            self.combo_events.addItem(text, event['id'])
            self.combo_events_gen.addItem(text, event['id'])
            self.combo_events_stats.addItem(text, event['id'])
        
        # Rafraîchir l'aperçu du template
        self.rafraichir_apercu_template()
        
        # Mettre à jour les stats accueil
        self.home_card_events.set_value(len(events))
        self.actualiser_stats_accueil()
    
    def appliquer_filtres_evenements(self):
        """Appliquer les filtres sur la liste des événements"""
        if not hasattr(self, 'all_events'):
            return
        
        events = self.all_events
        
        # Filtre par nom
        filtre_nom = self.filter_nom.text().strip().lower()
        if filtre_nom:
            events = [e for e in events if filtre_nom in e['nom'].lower()]
        
        # Filtre par date
        date_debut = self.filter_date_debut.date().toString("yyyy-MM-dd")
        date_fin = self.filter_date_fin.date().toString("yyyy-MM-dd")
        events = [e for e in events if date_debut <= e['date'] <= date_fin]
        
        # Afficher les événements filtrés
        self.table_events.setRowCount(len(events))
        for i, event in enumerate(events):
            self.table_events.setItem(i, 0, QTableWidgetItem(str(event['id'])))
            self.table_events.setItem(i, 1, QTableWidgetItem(event['nom']))
            self.table_events.setItem(i, 2, QTableWidgetItem(event['date']))
            self.table_events.setItem(i, 3, QTableWidgetItem(event['heure']))
            self.table_events.setItem(i, 4, QTableWidgetItem(event['lieu'] or ''))
            self.table_events.setItem(i, 5, QTableWidgetItem(event['organisateur'] or ''))
            
            template_text = "❌ Aucun"
            if event['template_path']:
                nom_fichier = Path(event['template_path']).name
                template_text = f"🖼️ {nom_fichier}"
            self.table_events.setItem(i, 6, QTableWidgetItem(template_text))
    
    def reinitialiser_filtres_evenements(self):
        """Réinitialiser tous les filtres"""
        self.filter_nom.clear()
        self.filter_date_debut.setDate(QDate.currentDate().addMonths(-6))
        self.filter_date_fin.setDate(QDate.currentDate().addMonths(12))
        self.appliquer_filtres_evenements()
    
    def actualiser_stats_accueil(self):
        """Actualiser les statistiques de la page d'accueil"""
        try:
            total_invites = 0
            total_presents = 0
            
            events = self.db.obtenir_evenements()
            for event in events:
                stats = self.db.obtenir_statistiques(event['id'])
                total_invites += stats.get('total_invites', 0)
                total_presents += stats.get('presents', 0)
            
            self.home_card_invites.set_value(total_invites)
            self.home_card_presents.set_value(total_presents)
            self.home_card_pending.set_value(total_invites - total_presents)
        except:
            pass
    
    # ============= INVITÉS =============
    
    def rafraichir_invites(self):
        """Rafraîchir la liste des invités"""
        if self.combo_events.currentIndex() < 0:
            self.table_invites.setRowCount(0)
            return
        
        event_id = self.combo_events.currentData()
        invites = self.db.obtenir_invites(event_id)
        
        # Stocker pour les filtres
        self.all_invites = invites
        
        # Rafraîchir le filtre des tables
        if hasattr(self, 'filter_invite_table'):
            self.filter_invite_table.blockSignals(True)
            self.filter_invite_table.clear()
            self.filter_invite_table.addItem("Toutes", None)
            tables = self.db.obtenir_tables(event_id)
            for table in tables:
                self.filter_invite_table.addItem(f"{table['nom']}", table['id'])
            self.filter_invite_table.blockSignals(False)
        
        # Réinitialiser les filtres
        if hasattr(self, 'filter_invite_nom'):
            self.filter_invite_nom.clear()
            self.filter_invite_statut.setCurrentIndex(0)
        
        # Afficher dans le tableau
        self.afficher_invites_dans_table(invites)
    
    def ouvrir_gestion_tables(self):
        """Ouvrir le dialogue de gestion des tables"""
        from PyQt5.QtWidgets import QDialog, QTableWidget, QHeaderView
        
        if self.combo_events.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner un événement")
            return
        
        event_id = self.combo_events.currentData()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Gestion des tables")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("🪑 Gestion des tables")
        title.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Formulaire d'ajout
        form_layout = QHBoxLayout()
        
        self.dialog_table_nom = QLineEdit()
        self.dialog_table_nom.setPlaceholderText("Nom de la table (ex: Table 1, VIP...)")
        self.appliquer_style_input(self.dialog_table_nom)
        form_layout.addWidget(self.dialog_table_nom)
        
        self.dialog_table_capacite = QSpinBox()
        self.dialog_table_capacite.setMinimum(1)
        self.dialog_table_capacite.setMaximum(50)
        self.dialog_table_capacite.setValue(10)
        self.dialog_table_capacite.setPrefix("Capacité: ")
        self.appliquer_style_input(self.dialog_table_capacite)
        form_layout.addWidget(self.dialog_table_capacite)
        
        btn_ajouter_table = QPushButton("➕ Ajouter")
        btn_ajouter_table.setCursor(Qt.PointingHandCursor)
        btn_ajouter_table.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
                color: white;
                border: none;
                padding: 12px 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['primary_dark']};
            }}
        """)
        btn_ajouter_table.clicked.connect(lambda: self.ajouter_table_dialog(event_id, dialog))
        form_layout.addWidget(btn_ajouter_table)
        
        layout.addLayout(form_layout)
        
        # Tableau des tables
        self.table_tables = QTableWidget()
        self.table_tables.setColumnCount(5)
        self.table_tables.setHorizontalHeaderLabels(["ID", "Nom", "Capacité", "Invités", "Actions"])
        self.appliquer_style_table(self.table_tables)
        self.table_tables.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table_tables)
        
        # Charger les tables
        self.rafraichir_tables_dialog(event_id)
        
        # Bouton fermer
        btn_fermer = QPushButton("Fermer")
        btn_fermer.setCursor(Qt.PointingHandCursor)
        btn_fermer.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['text_muted']}50;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['sidebar']};
            }}
        """)
        btn_fermer.clicked.connect(dialog.accept)
        layout.addWidget(btn_fermer)
        
        dialog.exec_()
        
        # Rafraîchir après fermeture
        self.rafraichir_invites()
    
    def ajouter_table_dialog(self, event_id, dialog):
        """Ajouter une table depuis le dialogue"""
        nom = self.dialog_table_nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de la table est requis")
            return
        
        capacite = self.dialog_table_capacite.value()
        
        table_id = self.db.ajouter_table(event_id, nom, capacite)
        if table_id:
            self.dialog_table_nom.clear()
            self.dialog_table_capacite.setValue(10)
            self.rafraichir_tables_dialog(event_id)
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout de la table")
    
    def rafraichir_tables_dialog(self, event_id):
        """Rafraîchir le tableau des tables dans le dialogue"""
        tables = self.db.obtenir_tables(event_id)
        self.table_tables.setRowCount(len(tables))
        
        for i, table in enumerate(tables):
            self.table_tables.setItem(i, 0, QTableWidgetItem(str(table['id'])))
            self.table_tables.setItem(i, 1, QTableWidgetItem(table['nom']))
            self.table_tables.setItem(i, 2, QTableWidgetItem(str(table['capacite'])))
            nb_personnes = table['nb_personnes'] or 0
            self.table_tables.setItem(i, 3, QTableWidgetItem(f"{nb_personnes}/{table['capacite']}"))
            
            # Bouton supprimer
            btn_suppr = QPushButton("🗑️")
            btn_suppr.setCursor(Qt.PointingHandCursor)
            btn_suppr.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['danger']};
                    color: white;
                    border: none;
                    padding: 5px 10px;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
            """)
            btn_suppr.clicked.connect(lambda checked, tid=table['id'], eid=event_id: self.supprimer_table_dialog(tid, eid))
            self.table_tables.setCellWidget(i, 4, btn_suppr)
    
    def supprimer_table_dialog(self, table_id, event_id):
        """Supprimer une table"""
        reponse = QMessageBox.question(
            self, "Confirmation",
            "Supprimer cette table ? Les invités seront désassignés.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            if self.db.supprimer_table(table_id):
                self.rafraichir_tables_dialog(event_id)
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression")
    
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
        
        generator = InvitationGenerator(template_path=event['template_path'])
        
        self.log_gen.clear()
        self.log_gen.append(f"🎨 Génération de {len(invites)} invitations...")
        self.progress_gen.setMaximum(len(invites))
        self.progress_gen.setValue(0)
        
        for i, invite in enumerate(invites):
            try:
                invite_data = {
                    'id': invite['id'],
                    'nom': invite['nom'],
                    'prenom': invite['prenom'],
                    'titre': invite['titre'] or '',
                    'categorie': invite['categorie'],
                    'evenement': {
                        'nom': event['nom'],
                        'date': event['date'],
                        'heure': event['heure'],
                        'lieu': event['lieu']
                    }
                }
                
                path, qr_code = generator.creer_invitation(invite_data)
                self.db.mettre_a_jour_invite(invite['id'], qr_code=qr_code, invitation_path=path)
                self.log_gen.append(f"✅ {invite['prenom']} {invite['nom']} - {path}")
                
            except Exception as e:
                self.log_gen.append(f"❌ Erreur pour {invite['prenom']} {invite['nom']}: {e}")
            
            self.progress_gen.setValue(i + 1)
            QApplication.processEvents()
        
        self.log_gen.append(f"\n✨ Génération terminée!")
        QMessageBox.information(self, "Succès", f"{len(invites)} invitations générées!")
        self.rafraichir_invites()
    
    def exporter_invitations_pdf(self):
        """Exporter toutes les invitations générées d'un événement dans un PDF."""
        if self.combo_events_gen.currentIndex() < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un événement")
            return
        
        event_id = self.combo_events_gen.currentData()
        event = self.db.obtenir_evenement(event_id)
        invites = self.db.obtenir_invites(event_id)
        
        invitation_paths = []
        for invite in invites:
            path = invite['invitation_path']
            if path and Path(path).exists():
                invitation_paths.append(Path(path))
        
        if not invitation_paths:
            QMessageBox.warning(
                self,
                "Aucune invitation",
                "Aucune invitation générée n'a été trouvée pour cet événement.\n"
                "Générez d'abord les invitations, puis relancez l'export PDF."
            )
            return
        
        try:
            from PIL import Image
            from reportlab.pdfgen import canvas as pdf_canvas
            
            nom_event = event['nom'] if event else "evenement"
            event_dir_name = InvitationGenerator.nettoyer_nom_dossier(nom_event)
            dossier = INVITATIONS_DIR / event_dir_name
            dossier.mkdir(parents=True, exist_ok=True)
            output_path = dossier / f"Invitations-{event_dir_name}.pdf"
            
            first_img = Image.open(invitation_paths[0])
            first_dpi = first_img.info.get('dpi', (300, 300))
            first_dpi_x = first_dpi[0] if first_dpi and first_dpi[0] else 300
            first_dpi_y = first_dpi[1] if first_dpi and first_dpi[1] else 300
            first_page_size = (
                first_img.width / first_dpi_x * 72,
                first_img.height / first_dpi_y * 72
            )
            first_img.close()
            
            pdf = pdf_canvas.Canvas(str(output_path), pagesize=first_page_size)
            
            for image_path in invitation_paths:
                with Image.open(image_path) as img:
                    dpi = img.info.get('dpi', (300, 300))
                    dpi_x = dpi[0] if dpi and dpi[0] else 300
                    dpi_y = dpi[1] if dpi and dpi[1] else 300
                    page_width = img.width / dpi_x * 72
                    page_height = img.height / dpi_y * 72
                
                pdf.setPageSize((page_width, page_height))
                pdf.drawImage(str(image_path), 0, 0, width=page_width, height=page_height)
                pdf.showPage()
            
            pdf.save()
            
            self.log_gen.append(f"📄 PDF compilé: {output_path}")
            QMessageBox.information(
                self,
                "PDF généré",
                f"PDF compilé avec {len(invitation_paths)} invitation(s).\n\n{output_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", f"Impossible de créer le PDF:\n{str(e)}")
            self.log_gen.append(f"❌ Erreur PDF: {e}")
    
    # ============= STATISTIQUES =============
    
    def rafraichir_statistiques(self):
        """Rafraîchir les statistiques"""
        if self.combo_events_stats.currentIndex() < 0:
            return
        
        event_id = self.combo_events_stats.currentData()
        stats = self.db.obtenir_statistiques(event_id)
        
        self.stat_card_invites.set_value(stats['total_invites'])
        self.stat_card_personnes.set_value(stats['total_personnes'])
        self.stat_card_presents.set_value(f"{stats['presents']}/{stats['personnes_presentes']}")
        self.stat_card_taux.set_value(f"{stats['taux_presence']:.1f}%")
        
        tables = stats['par_table']
        self.table_stats_tables.setRowCount(len(tables))
        
        for i, (table_nom, data) in enumerate(tables.items()):
            self.table_stats_tables.setItem(i, 0, QTableWidgetItem(table_nom))
            self.table_stats_tables.setItem(i, 1, QTableWidgetItem(str(data['nombre'])))
            self.table_stats_tables.setItem(i, 2, QTableWidgetItem(str(data['total_personnes'])))
            self.table_stats_tables.setItem(i, 3, QTableWidgetItem(str(data['presents'])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
