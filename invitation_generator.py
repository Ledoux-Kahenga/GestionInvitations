"""
Générateur d'invitations à partir de templates PSD/images
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode
import uuid
import json
from pathlib import Path
from config import INVITATIONS_DIR, QRCODES_DIR, QR_CONFIG, INVITATION_CONFIG


class InvitationGenerator:
    """Génère des invitations personnalisées avec QR codes"""
    
    def __init__(self, template_path=None):
        """
        Initialiser le générateur
        
        Args:
            template_path: Chemin vers le template (PSD, PNG, JPG)
        """
        self.template_path = template_path
        self.template = None
        self.config = None
        
        if template_path and Path(template_path).exists():
            self.charger_template(template_path)
            self.charger_config(template_path)
    
    def charger_template(self, template_path):
        """Charger le template d'invitation"""
        try:
            # Charger l'image (supporte PSD avec psd-tools)
            if str(template_path).lower().endswith('.psd'):
                from psd_tools import PSDImage
                psd = PSDImage.open(template_path)
                self.template = psd.composite()
            else:
                self.template = Image.open(template_path)
            
            # Convertir en RGB si nécessaire
            if self.template.mode != 'RGB':
                self.template = self.template.convert('RGB')
            
            print(f"✅ Template chargé: {self.template.size}")
            return True
        
        except Exception as e:
            print(f"❌ Erreur chargement template: {e}")
            return False
    
    def charger_config(self, template_path):
        """Charger la configuration de positionnement du template"""
        config_path = Path(template_path).with_suffix('.json')
        
        print(f"🔍 Recherche configuration: {config_path}")
        print(f"   Fichier existe: {config_path.exists()}")
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration chargée: {len(self.config.get('elements', []))} éléments")
                print(f"   Éléments: {[e['id'] for e in self.config.get('elements', [])]}")
                return True
            except Exception as e:
                print(f"⚠️ Erreur chargement config: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"ℹ️ Aucune configuration trouvée à: {config_path}")
            print("   Utilisation du mode par défaut")
            return False
    
    def generer_qr_code(self, data, taille=200):
        """
        Générer un QR code
        
        Args:
            data: Données à encoder (ID unique de l'invité)
            taille: Taille du QR code en pixels
        
        Returns:
            Image PIL du QR code
        """
        qr = qrcode.QRCode(
            version=QR_CONFIG['version'],
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=QR_CONFIG['box_size'],
            border=QR_CONFIG['border'],
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((taille, taille))
        
        return qr_img
    
    def sauvegarder_qr_code(self, qr_img, invite_id):
        """Sauvegarder le QR code"""
        qr_path = QRCODES_DIR / f"qr_{invite_id}.png"
        qr_img.save(qr_path)
        return str(qr_path)
    
    def creer_invitation(self, invite_data, save_path=None):
        """
        Créer une invitation personnalisée
        
        Args:
            invite_data: Dictionnaire avec les infos de l'invité
                {
                    'id': int,
                    'nom': str,
                    'prenom': str,
                    'categorie': str,
                    'evenement': {
                        'nom': str,
                        'date': str,
                        'heure': str,
                        'lieu': str
                    }
                }
            save_path: Chemin de sauvegarde (optionnel)
        
        Returns:
            Chemin de l'invitation générée
        """
        if self.template is None:
            # Créer un template par défaut si aucun n'est chargé
            self.template = Image.new('RGB', (1748, 2480), color=(255, 255, 255))
        
        # Copier le template
        invitation = self.template.copy()
        draw = ImageDraw.Draw(invitation)
        
        # Générer QR code unique
        qr_data = f"INVITE-{invite_data['id']}-{uuid.uuid4().hex[:8]}"
        qr_img = self.generer_qr_code(qr_data, taille=300)
        
        # Sauvegarder le QR code séparément
        self.sauvegarder_qr_code(qr_img, invite_data['id'])
        
        # Si configuration existe, l'utiliser
        if self.config and 'elements' in self.config:
            self.appliquer_config(invitation, draw, invite_data, qr_img, qr_data)
        else:
            # Sinon, utiliser le mode par défaut
            self.appliquer_mode_defaut(invitation, draw, invite_data, qr_img, qr_data)
        
        # Sauvegarder l'invitation
        if save_path is None:
            save_path = INVITATIONS_DIR / f"invitation_{invite_data['id']}.jpg"
        
        invitation.save(save_path, quality=INVITATION_CONFIG['quality'], dpi=(INVITATION_CONFIG['dpi'], INVITATION_CONFIG['dpi']))
        
        return str(save_path), qr_data
    
    def appliquer_config(self, invitation, draw, invite_data, qr_img, qr_data):
        """Appliquer la configuration personnalisée"""
        # Mapper les IDs aux données
        data_map = {
            'nom_complet': f"{invite_data['prenom']} {invite_data['nom']}",
            'prenom': invite_data['prenom'],
            'nom': invite_data['nom'],
            'categorie': invite_data['categorie'],
            'event_nom': invite_data['evenement']['nom'],
            'event_date': invite_data['evenement']['date'],
            'event_heure': invite_data['evenement']['heure'],
            'event_lieu': invite_data['evenement']['lieu'],
            'qrcode': qr_img
        }
        
        # Appliquer chaque élément
        for elem in self.config['elements']:
            elem_id = elem['id']
            elem_type = elem['type']
            
            if elem_type == 'qr' and elem_id == 'qrcode':
                # Redimensionner et coller le QR code
                qr_resized = qr_img.resize((elem['width'], elem['height']))
                invitation.paste(qr_resized, (elem['x'], elem['y']))
            
            elif elem_type == 'text' and elem_id in data_map:
                # Dessiner le texte
                try:
                    font = ImageFont.truetype(
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        elem.get('font_size', 40)
                    )
                except:
                    font = ImageFont.load_default()
                
                # Convertir la couleur hex en RGB
                color = elem.get('color', '#000000')
                if color.startswith('#'):
                    color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                
                # Centrer le texte dans la zone
                text = str(data_map[elem_id])
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_x = elem['x'] + (elem['width'] - text_width) // 2
                text_y = elem['y'] + (elem['height'] - text_height) // 2
                
                draw.text((text_x, text_y), text, fill=color, font=font)
    
    def appliquer_mode_defaut(self, invitation, draw, invite_data, qr_img, qr_data):
        """Appliquer le mode par défaut (ancien comportement)"""
        
    def appliquer_mode_defaut(self, invitation, draw, invite_data, qr_img, qr_data):
        """Appliquer le mode par défaut (ancien comportement)"""
        # Charger les polices (utiliser police par défaut si erreur)
        try:
            font_titre = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            font_nom = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_texte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font_titre = ImageFont.load_default()
            font_nom = ImageFont.load_default()
            font_texte = ImageFont.load_default()
        
        # Positionner les éléments sur l'invitation
        width, height = invitation.size
        
        # Titre de l'événement (centré en haut)
        event_nom = invite_data['evenement']['nom']
        draw.text((width//2, 200), event_nom, fill=(46, 134, 171), font=font_titre, anchor="mm")
        
        # Nom de l'invité (centré)
        nom_complet = f"{invite_data['prenom']} {invite_data['nom']}"
        draw.text((width//2, 500), nom_complet, fill=(0, 0, 0), font=font_nom, anchor="mm")
        
        # Catégorie
        draw.text((width//2, 600), f"Catégorie: {invite_data['categorie']}", 
                  fill=(100, 100, 100), font=font_texte, anchor="mm")
        
        # Détails de l'événement
        y_pos = 800
        details = [
            f"📅 Date: {invite_data['evenement']['date']}",
            f"🕐 Heure: {invite_data['evenement']['heure']}",
            f"📍 Lieu: {invite_data['evenement']['lieu']}"
        ]
        
        for detail in details:
            draw.text((width//2, y_pos), detail, fill=(0, 0, 0), font=font_texte, anchor="mm")
            y_pos += 80
        
        # Coller le QR code (en bas à droite)
        qr_position = (width - 400, height - 400)
        invitation.paste(qr_img, qr_position)
        
        # Texte QR code
        draw.text((width - 250, height - 80), "Scannez pour valider", 
                  fill=(100, 100, 100), font=font_texte, anchor="mm")
    
    def creer_invitations_batch(self, invites_list):
        """
        Créer plusieurs invitations en batch
        
        Args:
            invites_list: Liste de dictionnaires d'invités
        
        Returns:
            Liste de chemins des invitations générées
        """
        invitations = []
        for invite in invites_list:
            try:
                path, qr = self.creer_invitation(invite)
                invitations.append({
                    'invite_id': invite['id'],
                    'path': path,
                    'qr_code': qr,
                    'success': True
                })
            except Exception as e:
                invitations.append({
                    'invite_id': invite['id'],
                    'error': str(e),
                    'success': False
                })
        
        return invitations
