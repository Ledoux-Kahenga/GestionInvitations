"""
Scanner de QR codes pour validation des invitations
"""
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from datetime import datetime
from database_model import InvitationModel


class QRScanner:
    """Scanner de QR codes avec caméra"""
    
    def __init__(self, camera_index=0):
        """
        Initialiser le scanner
        
        Args:
            camera_index: Index de la caméra (0 par défaut)
        """
        self.camera_index = camera_index
        self.cap = None
        self.db = InvitationModel()
        self.derniers_scans = set()  # Éviter les doubles scans
    
    def demarrer_camera(self):
        """Démarrer la caméra"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception("Impossible d'ouvrir la caméra")
        return True
    
    def arreter_camera(self):
        """Arrêter la caméra"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def scanner_qr_image(self, image):
        """
        Scanner un QR code dans une image
        
        Args:
            image: Image numpy array (BGR)
        
        Returns:
            Liste de données décodées
        """
        decoded_objects = decode(image)
        return decoded_objects
    
    def valider_invitation(self, qr_code, lieu="Entrée principale"):
        """
        Valider une invitation via son QR code
        
        Args:
            qr_code: Code QR scanné (peut contenir les infos formatées ou juste l'ID)
            lieu: Lieu du scan
        
        Returns:
            Dict avec le résultat de la validation
        """
        # Extraire l'ID technique du QR code
        # Le QR code peut être soit l'ancien format (INVITE-X-XXX) 
        # soit le nouveau format (texte multiligne avec ID: à la fin)
        qr_id = qr_code
        if '\n' in qr_code and 'ID:' in qr_code:
            # Nouveau format : extraire la ligne ID:
            for ligne in qr_code.split('\n'):
                if ligne.startswith('ID:'):
                    qr_id = ligne.replace('ID:', '').strip()
                    break
        
        # Vérifier si déjà scanné récemment (éviter doubles scans)
        if qr_id in self.derniers_scans:
            return {
                'valide': False,
                'message': '⚠️ QR code déjà scanné récemment',
                'invite': None
            }
        
        # Récupérer l'invité par l'ID technique
        invite = self.db.obtenir_invite_par_qr(qr_id)
        
        if not invite:
            return {
                'valide': False,
                'message': '❌ QR code invalide',
                'invite': None
            }
        
        # Vérifier le statut
        if invite['statut'] == 'présent':
            return {
                'valide': False,
                'message': f"⚠️ {invite['nom_complet']} déjà enregistré(e)",
                'invite': invite,
                'deja_present': True
            }
        
        # Enregistrer le scan
        scan_success = self.db.enregistrer_scan(invite['id'], lieu)
        
        if scan_success:
            # Ajouter aux scans récents (utiliser l'ID technique)
            self.derniers_scans.add(qr_id)
            
            # Calculer le nombre total de personnes
            nb_personnes = 1 + invite['nombre_accompagnants']
            
            return {
                'valide': True,
                'message': f"✅ Bienvenue {invite['nom_complet']}!",
                'invite': invite,
                'nb_personnes': nb_personnes,
                'categorie': invite['categorie']
            }
        else:
            return {
                'valide': False,
                'message': '❌ Erreur lors de l\'enregistrement',
                'invite': invite
            }
    
    def scanner_en_continu(self, callback=None):
        """
        Scanner en continu avec la caméra
        
        Args:
            callback: Fonction appelée quand un QR est détecté
                      callback(qr_data, validation_result)
        """
        if not self.cap or not self.cap.isOpened():
            self.demarrer_camera()
        
        print("🎥 Scanner actif. Appuyez sur 'q' pour quitter.")
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("❌ Erreur lecture caméra")
                break
            
            # Décoder les QR codes
            qr_codes = self.scanner_qr_image(frame)
            
            for qr in qr_codes:
                qr_data = qr.data.decode('utf-8')
                
                # Dessiner un rectangle autour du QR code
                points = qr.polygon
                if len(points) == 4:
                    pts = np.array(points, dtype=np.int32)
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                
                # Valider l'invitation
                validation = self.valider_invitation(qr_data)
                
                # Afficher le résultat sur l'image
                color = (0, 255, 0) if validation['valide'] else (0, 0, 255)
                cv2.putText(frame, validation['message'], 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, color, 2)
                
                # Callback personnalisé
                if callback:
                    callback(qr_data, validation)
                
                # Afficher les infos
                if validation['invite']:
                    invite = validation['invite']
                    y = 100
                    
                    # Nom de l'événement
                    if invite.get('nom_evenement'):
                        cv2.putText(frame, f"Evenement: {invite['nom_evenement']}", 
                                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        y += 40
                    
                    # Nom complet de l'invité
                    cv2.putText(frame, f"Invite: {invite['nom_complet']}", 
                               (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    y += 40
                    
                    # Table
                    table_info = invite.get('nom_table') or 'Non assignée'
                    cv2.putText(frame, f"Table: {table_info}", 
                               (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    y += 40
                    
                    # Date de l'événement
                    if invite.get('date_evenement'):
                        cv2.putText(frame, f"Date: {invite['date_evenement']}", 
                                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        y += 40
                    
                    if 'nb_personnes' in validation:
                        cv2.putText(frame, f"Personnes: {validation['nb_personnes']}", 
                                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Afficher le flux
            cv2.imshow('Scanner QR - Appuyez sur Q pour quitter', frame)
            
            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.arreter_camera()
    
    def nettoyer_scans_recents(self):
        """Nettoyer la liste des scans récents"""
        self.derniers_scans.clear()
    
    def scanner_fichier_image(self, image_path):
        """
        Scanner un QR code depuis un fichier image
        
        Args:
            image_path: Chemin vers l'image
        
        Returns:
            Résultat de la validation
        """
        image = cv2.imread(str(image_path))
        if image is None:
            return {
                'valide': False,
                'message': '❌ Impossible de lire l\'image',
                'invite': None
            }
        
        qr_codes = self.scanner_qr_image(image)
        
        if not qr_codes:
            return {
                'valide': False,
                'message': '❌ Aucun QR code détecté',
                'invite': None
            }
        
        # Valider le premier QR code trouvé
        qr_data = qr_codes[0].data.decode('utf-8')
        return self.valider_invitation(qr_data)


# Exemple d'utilisation
if __name__ == "__main__":
    scanner = QRScanner()
    
    def on_qr_detected(qr_data, validation):
        """Callback appelé quand un QR est détecté"""
        print(f"\n📱 QR détecté: {qr_data}")
        print(f"Résultat: {validation['message']}")
        
        if validation['invite']:
            invite = validation['invite']
            print(f"Événement: {invite.get('nom_evenement', 'N/A')}")
            print(f"Invité: {invite['nom_complet']}")
            print(f"Table: {invite.get('nom_table') or 'Non assignée'}")
            print(f"Date: {invite.get('date_evenement', 'N/A')}")
            print(f"Catégorie: {invite['categorie']}")
    
    try:
        scanner.scanner_en_continu(callback=on_qr_detected)
    except KeyboardInterrupt:
        print("\n👋 Scanner arrêté")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        scanner.arreter_camera()
