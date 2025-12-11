"""
Sélecteur de fichier simple pour éviter les crashs
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QListWidget, QLabel, QLineEdit)
from PyQt5.QtCore import Qt
from pathlib import Path


class SimpleFileSelector(QDialog):
    """Sélecteur de fichier simple sans dialogue natif"""
    
    def __init__(self, directory, file_filter="*", parent=None):
        super().__init__(parent)
        self.selected_file = None
        self.directory = Path(directory)
        
        self.setWindowTitle("Sélectionner un fichier")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        # Chemin actuel
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Dossier:"))
        self.path_label = QLineEdit(str(self.directory))
        self.path_label.setReadOnly(True)
        path_layout.addWidget(self.path_label)
        layout.addLayout(path_layout)
        
        # Liste des fichiers
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.accept_file)
        layout.addWidget(self.file_list)
        
        # Charger les fichiers
        self.load_files(file_filter)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Sélectionner")
        btn_ok.clicked.connect(self.accept_file)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_files(self, file_filter):
        """Charger la liste des fichiers"""
        self.file_list.clear()
        
        if not self.directory.exists():
            return
        
        # Extensions acceptées
        extensions = ['.png', '.jpg', '.jpeg', '.psd']
        
        for file_path in sorted(self.directory.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                self.file_list.addItem(file_path.name)
    
    def accept_file(self):
        """Accepter le fichier sélectionné"""
        current_item = self.file_list.currentItem()
        if current_item:
            self.selected_file = str(self.directory / current_item.text())
            self.accept()
    
    @staticmethod
    def get_open_filename(parent, title, directory, file_filter=""):
        """Méthode statique pour remplacer QFileDialog.getOpenFileName"""
        dialog = SimpleFileSelector(directory, file_filter, parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.selected_file, None
        return None, None
