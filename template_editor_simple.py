"""
Version simplifiée de l'éditeur pour test
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path
from config import TEMPLATES_DIR
from simple_file_selector import SimpleFileSelector


class TemplateEditorSimple(QDialog):
    """Version simple de l'éditeur pour tester"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_path = None
        
        self.setWindowTitle("Éditeur de Template - Version Simple")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialiser une interface minimale"""
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("<h1>Éditeur de Template</h1>")
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)
        
        # Message
        self.message = QLabel("Cliquez sur 'Charger Template' pour commencer")
        self.message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_load = QPushButton("📂 Charger Template")
        btn_load.clicked.connect(self.select_template)
        btn_layout.addWidget(btn_load)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def select_template(self):
        """Sélectionner un template"""
        try:
            # Utiliser notre sélecteur personnalisé au lieu de QFileDialog
            file_path, _ = SimpleFileSelector.get_open_filename(
                self,
                "Sélectionner un template",
                str(TEMPLATES_DIR),
                "Images"
            )
            
            if file_path:
                self.template_path = file_path
                self.message.setText(f"Template chargé :\n{Path(file_path).name}")
                QMessageBox.information(self, "Succès", 
                    "Template chargé avec succès!\n\n"
                    "Le sélecteur personnalisé fonctionne.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
            print(f"Erreur select_template: {e}")
            import traceback
            traceback.print_exc()
