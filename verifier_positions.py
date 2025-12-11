"""
Script de test pour vérifier la correspondance des positions
"""
import json
from pathlib import Path

# Lister tous les fichiers JSON de configuration
config_dir = Path("templates")
json_files = list(config_dir.glob("*.json"))

print("🔍 Vérification des fichiers de configuration\n")
print("=" * 70)

for json_file in json_files:
    print(f"\n📄 Fichier: {json_file.name}")
    print("-" * 70)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Afficher les infos du template
        template_width = config.get('template_width', 'Non défini')
        template_height = config.get('template_height', 'Non défini')
        scale_factor = config.get('scale_factor', 'Non défini')
        
        print(f"  Template: {template_width} x {template_height} px")
        print(f"  Échelle sauvegardée: {scale_factor}")
        print(f"  Nombre d'éléments: {len(config.get('elements', []))}")
        
        # Vérifier chaque élément
        print(f"\n  Éléments:")
        for i, elem in enumerate(config.get('elements', []), 1):
            print(f"    {i}. {elem.get('label', 'Sans nom')} ({elem.get('type', '?')})")
            print(f"       Position: X={elem.get('x', 0)}, Y={elem.get('y', 0)}")
            print(f"       Taille: {elem.get('width', 0)} x {elem.get('height', 0)} px")
            print(f"       Police: {elem.get('font_size', 'N/A')} / Couleur: {elem.get('color', 'N/A')}")
            
            # Vérifier les valeurs aberrantes
            warnings = []
            if elem.get('width', 0) < 50 and elem.get('type') == 'qr':
                warnings.append("⚠️ QR code trop petit")
            if elem.get('height', 0) < 20:
                warnings.append("⚠️ Hauteur très petite")
            if elem.get('x', 0) < 0 or elem.get('y', 0) < 0:
                warnings.append("❌ Position négative")
            if isinstance(template_width, int) and elem.get('x', 0) > template_width:
                warnings.append("❌ Position X hors limites")
            if isinstance(template_height, int) and elem.get('y', 0) > template_height:
                warnings.append("❌ Position Y hors limites")
            
            if warnings:
                for warning in warnings:
                    print(f"       {warning}")
        
        # Vérifier le chemin du template
        template_path = config.get('template_path', '')
        if template_path:
            template_file = Path(template_path)
            if not template_file.exists():
                # Essayer avec juste le nom du fichier
                local_template = config_dir / template_file.name
                if local_template.exists():
                    print(f"\n  ℹ️  Template trouvé localement: {local_template}")
                else:
                    print(f"\n  ⚠️  Template introuvable: {template_path}")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Erreur de lecture JSON: {e}")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")

print("\n" + "=" * 70)
print("\n✅ Vérification terminée\n")

# Recommandations
print("💡 RECOMMANDATIONS:")
print("  1. Les positions X, Y doivent être >= 0")
print("  2. Les QR codes doivent faire au moins 200x200 px")
print("  3. Les zones de texte doivent avoir une largeur >= 200 px")
print("  4. Vérifiez que X+largeur et Y+hauteur ne dépassent pas les dimensions du template")
print("  5. Si les positions ne correspondent pas, rechargez le template dans l'éditeur")
