"""
Génère un PDF : guide des éléments gratuits pour une app mobile de lecture QR.
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT = Path(__file__).resolve().parent / "Guide_App_Mobile_QR.pdf"

# Palette
BLEU = HexColor("#1a365d")
BLEU_CLAIR = HexColor("#2b6cb0")
VERT = HexColor("#276749")
ORANGE = HexColor("#c05621")
GRIS = HexColor("#4a5568")
GRIS_CLAIR = HexColor("#edf2f7")
ROUGE = HexColor("#c53030")
FOND_TABLE = HexColor("#f7fafc")


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"],
            fontSize=26, textColor=white, alignment=TA_CENTER,
            spaceAfter=12, fontName="Helvetica-Bold", leading=32
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"],
            fontSize=13, textColor=HexColor("#bee3f8"), alignment=TA_CENTER,
            spaceAfter=6, fontName="Helvetica", leading=18
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"],
            fontSize=16, textColor=BLEU, spaceBefore=16, spaceAfter=10,
            fontName="Helvetica-Bold", borderPadding=4
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"],
            fontSize=12, textColor=BLEU_CLAIR, spaceBefore=12, spaceAfter=6,
            fontName="Helvetica-Bold"
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=10, textColor=GRIS, alignment=TA_JUSTIFY,
            spaceAfter=6, leading=14, fontName="Helvetica"
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontSize=10, textColor=GRIS, leftIndent=12,
            spaceAfter=3, leading=13, fontName="Helvetica"
        ),
        "note": ParagraphStyle(
            "note", parent=base["Normal"],
            fontSize=9, textColor=ORANGE, spaceBefore=4, spaceAfter=8,
            leading=12, fontName="Helvetica-Oblique"
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontSize=8, textColor=GRIS, alignment=TA_CENTER
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"],
            fontSize=8.5, textColor=GRIS, leading=11, fontName="Helvetica"
        ),
        "cell_b": ParagraphStyle(
            "cell_b", parent=base["Normal"],
            fontSize=8.5, textColor=BLEU, leading=11, fontName="Helvetica-Bold"
        ),
        "ok": ParagraphStyle(
            "ok", parent=base["Normal"],
            fontSize=9, textColor=VERT, leading=12, fontName="Helvetica-Bold"
        ),
    }
    return s


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BLEU_CLAIR)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, A4[1] - 1.2 * cm, A4[0] - 2 * cm, A4[1] - 1.2 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, A4[1] - 1 * cm, "GestionInvitations — App mobile QR")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1 * cm, "Guide gratuit")
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLEU)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(BLEU_CLAIR)
    canvas.rect(0, A4[1] * 0.35, A4[0], A4[1] * 0.08, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.62, "Application mobile")
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.56, "lecture de QR codes")
    canvas.setFont("Helvetica", 12)
    canvas.setFillColor(HexColor("#bee3f8"))
    canvas.drawCentredString(
        A4[0] / 2, A4[1] * 0.48,
        "Éléments gratuits nécessaires : API, base de données, serveur…"
    )
    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawCentredString(A4[0] / 2, A4[1] * 0.38, "Projet GestionInvitations")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(HexColor("#a0aec0"))
    canvas.drawCentredString(A4[0] / 2, 2.5 * cm, "Document technique — Stack 100 % gratuite recommandée")
    canvas.restoreState()


def make_table(headers, rows, col_widths, s):
    data = [[Paragraph(h, s["cell_b"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), s["cell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLEU),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("BACKGROUND", (0, 1), (-1, -1), FOND_TABLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [FOND_TABLE, white]),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#cbd5e0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    # Override header paragraph color via style already blue on dark — recreate header white
    for i, h in enumerate(headers):
        data[0][i] = Paragraph(
            f'<font color="white"><b>{h}</b></font>',
            ParagraphStyle("hw", fontSize=8.5, fontName="Helvetica-Bold", leading=11)
        )
    return t


def build():
    s = styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title="Guide App Mobile QR — GestionInvitations",
        author="GestionInvitations",
    )
    story = []
    w = A4[0] - 4 * cm

    # Page 1 starts after cover (page 0 drawn separately)
    story.append(Paragraph("1. Objectif", s["h1"]))
    story.append(Paragraph(
        "Créer une <b>application mobile dédiée</b> (Android / iOS) pour scanner les QR codes "
        "des invitations générées par GestionInvitations, valider l’entrée des invités en temps "
        "réel, et synchroniser le statut (scanné / déjà entré) avec une base centrale.",
        s["body"]
    ))
    story.append(Paragraph(
        "Aujourd’hui, le scanner est intégré au PC (OpenCV + SQLite locale). "
        "L’app mobile nécessite un <b>backend en ligne</b> : le téléphone ne peut pas lire "
        "directement le fichier SQLite du PC.",
        s["note"]
    ))

    story.append(Paragraph("2. Architecture cible (vue d’ensemble)", s["h1"]))
    story.append(Paragraph(
        "1. <b>App PC GestionInvitations</b> — crée les événements, invités, génère les QR "
        "(format actuel : <font face='Courier'>INVITE-{id}-{hash}</font>).<br/>"
        "2. <b>API / serveur</b> — reçoit les données d’invités et répond aux scans mobiles.<br/>"
        "3. <b>Base de données cloud</b> — stocke invités, QR, statut de scan, historique.<br/>"
        "4. <b>App mobile</b> — caméra + lecture QR + appel API + affichage OK / Refusé.<br/>"
        "5. <b>(Optionnel)</b> Tableau de bord web pour suivre les entrées en live.",
        s["body"]
    ))

    story.append(Paragraph("3. Ce dont vous avez besoin (checklist)", s["h1"]))
    story.append(make_table(
        ["Élément", "Rôle", "Obligatoire ?", "Option gratuite"],
        [
            ["Application mobile", "Scanner QR + UI agent d’accueil", "Oui", "Flutter / React Native / Expo"],
            ["API REST (backend)", "Valider un QR, marquer l’entrée", "Oui", "FastAPI / Flask / Node sur Render ou Railway"],
            ["Base de données", "Invités, QR, scans, événements", "Oui", "PostgreSQL (Neon / Supabase) ou SQLite hébergé"],
            ["Hébergement serveur", "Faire tourner l’API 24/7 le jour J", "Oui", "Render Free, Railway Free, Fly.io Free"],
            ["Authentification agents", "Empêcher n’importe qui de valider", "Fortement recommandé", "JWT + login simple / Firebase Auth"],
            ["Stockage fichiers", "Photos / logs (optionnel)", "Non", "Cloudflare R2 free tier / local"],
            ["Nom de domaine", "URL propre pour l’API", "Non", "Sous-domaine gratuit *.onrender.com"],
            ["Push notifications", "Alerte double entrée", "Non", "Firebase Cloud Messaging (gratuit)"],
            ["CDN / HTTPS", "Sécuriser les appels API", "Inclus", "Fourni par l’hébergeur"],
            ["Compte développeur stores", "Publier sur Play Store / App Store", "Si publication", "Play : 25 $ une fois / Apple : 99 $/an"],
        ],
        [3.2 * cm, 4.2 * cm, 2.8 * cm, 6.5 * cm],
        s,
    ))
    story.append(Paragraph(
        "Note : pour un usage interne (APK installé sur les téléphones du staff), "
        "vous n’avez pas besoin de publier sur les stores.",
        s["note"]
    ))

    story.append(Paragraph("4. Stack gratuite recommandée (simple et réaliste)", s["h1"]))
    story.append(Paragraph(
        "Proposition adaptée à votre projet Python existant — coût = <b>0 €</b> "
        "dans les limites des free tiers.",
        s["body"]
    ))
    story.append(make_table(
        ["Couche", "Choix recommandé", "Pourquoi", "Limite free typique"],
        [
            ["App mobile", "Flutter (Dart) ou Expo (React Native)", "Caméra QR mature, 1 code → Android+iOS", "Illimité (outil open source)"],
            ["Lecture QR", "mobile_scanner (Flutter) / expo-camera", "Gratuit, open source", "—"],
            ["API", "FastAPI (Python)", "Même langage que GestionInvitations", "Selon hébergeur"],
            ["Base", "PostgreSQL via Supabase ou Neon", "Gratuit, backup, SQL familier", "~500 Mo / projets limités"],
            ["Hébergement API", "Render.com (Web Service Free)", "HTTPS, déploiement Git", "Veille après inactivité (~15 min)"],
            ["Auth staff", "Token JWT + PIN événement", "Simple, sans service payant", "—"],
            ["Sync PC → cloud", "Export / sync depuis l’app desktop", "Réutilise votre SQLite actuelle", "—"],
        ],
        [2.8 * cm, 4.5 * cm, 5.2 * cm, 4.2 * cm],
        s,
    ))

    story.append(Paragraph("5. Alternative « ultra-simple » : Firebase / Supabase seuls", s["h1"]))
    story.append(Paragraph(
        "Si vous voulez éviter de coder un serveur API dédié :",
        s["body"]
    ))
    story.append(Paragraph("• <b>Supabase</b> (gratuit) : base PostgreSQL + API auto-générée + auth.", s["bullet"]))
    story.append(Paragraph("• <b>Firebase</b> (gratuit) : Firestore + Auth + règles de sécurité.", s["bullet"]))
    story.append(Paragraph(
        "L’app mobile lit/écrit directement dans la base via le SDK. "
        "L’app PC exporte les invités (JSON/CSV) vers Supabase/Firebase. "
        "Moins de contrôle métier, mais plus rapide à lancer.",
        s["body"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("6. API minimale à prévoir (endpoints)", s["h1"]))
    story.append(Paragraph(
        "Que vous codiez FastAPI ou utilisiez Supabase, voici les opérations indispensables :",
        s["body"]
    ))
    story.append(make_table(
        ["Méthode", "Endpoint / action", "Entrée", "Sortie"],
        [
            ["POST", "Connexion agent", "identifiant + PIN événement", "token JWT"],
            ["GET", "Infos événement", "event_id", "nom, date, nb invités"],
            ["POST", "Scanner / valider QR", "qr_code, lieu, agent_id", "valide + infos invité + message"],
            ["GET", "Statistiques live", "event_id", "entrés / restants / refus"],
            ["POST", "Sync invités (PC)", "liste invités + QR", "accusé de réception"],
            ["GET", "Historique scans", "event_id", "liste horodatée"],
        ],
        [2.2 * cm, 4.5 * cm, 4.5 * cm, 5.5 * cm],
        s,
    ))
    story.append(Paragraph("6.1 Réponses typiques du scan", s["h2"]))
    story.append(Paragraph(
        "• <b>OK</b> — premier scan : afficher nom, titre, table, accompagnants ; marquer <i>statut = scanné</i>.<br/>"
        "• <b>Déjà entré</b> — QR déjà validé : afficher heure du 1er scan (anti-fraude).<br/>"
        "• <b>Invalide</b> — QR inconnu ou mauvais événement.<br/>"
        "• <b>Événement fermé</b> — hors créneau autorisé (optionnel).",
        s["body"]
    ))

    story.append(Paragraph("7. Base de données — tables essentielles", s["h1"]))
    story.append(make_table(
        ["Table", "Champs clés", "Remarque"],
        [
            ["evenements", "id, nom, date, lieu, pin_agent, actif", "Correspond à votre modèle actuel"],
            ["invites", "id, evenement_id, titre, nom, table, qr_code UNIQUE, statut, date_scan", "Migrer depuis SQLite PC"],
            ["scans", "id, invite_id, agent_id, lieu, horodatage, resultat", "Historique (audit)"],
            ["agents", "id, nom, login, hash_mdp, role", "Staff entrée / contrôle"],
        ],
        [3 * cm, 9 * cm, 4.7 * cm],
        s,
    ))
    story.append(Paragraph(
        "Votre format QR actuel <font face='Courier'>INVITE-{id}-{hash}</font> peut être conservé : "
        "il suffit de synchroniser la colonne <font face='Courier'>qr_code</font> vers le cloud.",
        s["note"]
    ))

    story.append(Paragraph("8. Serveur / hébergement — options 100 % gratuites", s["h1"]))
    story.append(make_table(
        ["Service", "Offre", "Avantage", "Attention"],
        [
            ["Render", "Web Service Free", "Simple, HTTPS, Git deploy", "S’endort après ~15 min d’inactivité"],
            ["Railway", "Crédit mensuel gratuit", "Rapide à lancer", "Crédit limité / mois"],
            ["Fly.io", "Free allowance", "Proche des utilisateurs", "Carte parfois demandée"],
            ["Supabase", "Free tier", "DB + API + auth inclus", "Limite de projets / bande passante"],
            ["Neon", "Postgres serverless free", "Excellente pour FastAPI", "À coupler avec un hébergeur API"],
            ["Cloudflare Tunnel", "Gratuit", "Exposer un PC local sans VPS", "PC doit rester allumé le jour J"],
            ["ngrok (free)", "Tunnel temporaire", "Tests rapides", "URL change ; pas idéal en prod"],
        ],
        [2.8 * cm, 3.5 * cm, 4.5 * cm, 5.9 * cm],
        s,
    ))
    story.append(Paragraph(
        "Astuce jour J : si Render s’endort, faites un « ping » toutes les 10 min "
        "(cron gratuit UptimeRobot) ou gardez le PC allumé avec Cloudflare Tunnel + API locale.",
        s["note"]
    ))

    story.append(Paragraph("9. Application mobile — éléments techniques", s["h1"]))
    story.append(Paragraph("Écrans indispensables", s["h2"]))
    story.append(Paragraph("• Connexion agent (PIN / mot de passe événement).", s["bullet"]))
    story.append(Paragraph("• Choix de l’événement actif.", s["bullet"]))
    story.append(Paragraph("• Scanner caméra plein écran + flash.", s["bullet"]))
    story.append(Paragraph("• Résultat : vert (OK) / orange (déjà entré) / rouge (invalide).", s["bullet"]))
    story.append(Paragraph("• Compteur live : entrés / total.", s["bullet"]))
    story.append(Paragraph("• Mode hors-ligne léger (option) : file d’attente des scans si réseau faible.", s["bullet"]))

    story.append(Paragraph("Permissions & matériel", s["h2"]))
    story.append(Paragraph("• Permission caméra (obligatoire).", s["bullet"]))
    story.append(Paragraph("• Internet (Wi‑Fi / 4G sur site).", s["bullet"]))
    story.append(Paragraph("• Téléphones Android récents suffisent ; pas besoin de terminal payant.", s["bullet"]))

    story.append(PageBreak())
    story.append(Paragraph("10. Lien avec GestionInvitations (PC)", s["h1"]))
    story.append(Paragraph(
        "Sans modifier toute l’app desktop, le flux minimal est :",
        s["body"]
    ))
    story.append(Paragraph(
        "1. Générer les invitations + QR comme aujourd’hui (SQLite locale).<br/>"
        "2. Ajouter un bouton <b>« Synchroniser vers le cloud »</b> qui envoie "
        "événement + invités + qr_code vers l’API.<br/>"
        "3. Le jour J, seuls les téléphones scannent ; le PC peut afficher les stats live.<br/>"
        "4. Après l’événement, optionnellement rapatrier les <font face='Courier'>date_scan</font> "
        "vers la base locale.",
        s["body"]
    ))

    story.append(Paragraph("11. Sécurité (même en gratuit)", s["h1"]))
    story.append(Paragraph("• HTTPS uniquement (fourni par Render / Supabase).", s["bullet"]))
    story.append(Paragraph("• Token JWT avec expiration courte pour les agents.", s["bullet"]))
    story.append(Paragraph("• PIN unique par événement (changeable).", s["bullet"]))
    story.append(Paragraph("• QR unique et non prévisible (votre hash actuel convient).", s["bullet"]))
    story.append(Paragraph("• Journal des scans (qui a validé, quand, où).", s["bullet"]))
    story.append(Paragraph("• Ne jamais embarquer la base complète en clair dans l’APK.", s["bullet"]))

    story.append(Paragraph("12. Budget réel : gratuit vs payant", s["h1"]))
    story.append(make_table(
        ["Poste", "Gratuit possible ?", "Quand payer ?"],
        [
            ["Développement (Flutter / FastAPI)", "Oui (open source)", "Si vous engagez un développeur"],
            ["API + DB (petits événements)", "Oui (free tiers)", "Si > quelques milliers d’invités / mois ou uptime critique"],
            ["Distribution APK interne", "Oui", "—"],
            ["Google Play", "Non (25 $ une fois)", "Si publication publique"],
            ["Apple App Store", "Non (99 $/an)", "Si iPhone staff via store officiel"],
            ["SMS / WhatsApp d’invitation", "Hors scope QR", "Services SMS payants"],
        ],
        [5.5 * cm, 5 * cm, 6.2 * cm],
        s,
    ))

    story.append(Paragraph("13. Plan de mise en œuvre suggéré", s["h1"]))
    story.append(make_table(
        ["Étape", "Livrable", "Durée indicative"],
        [
            ["1", "Créer projet Supabase ou Postgres + schéma tables", "1–2 jours"],
            ["2", "API FastAPI : sync + validate QR", "2–4 jours"],
            ["3", "App mobile Expo/Flutter : login + scan + résultat", "1–2 semaines"],
            ["4", "Bouton sync dans GestionInvitations (PC)", "1–2 jours"],
            ["5", "Test terrain (Wi‑Fi, double scan, hors ligne)", "2–3 jours"],
            ["6", "APK pour staff + checklist jour J", "1 jour"],
        ],
        [2 * cm, 10.5 * cm, 4.2 * cm],
        s,
    ))

    story.append(Paragraph("14. Recommandation finale", s["h1"]))
    story.append(Paragraph(
        "Pour démarrer <b>sans budget</b> et rester cohérent avec votre stack Python :",
        s["body"]
    ))
    story.append(Paragraph(
        "• <b>Mobile</b> : Flutter ou Expo<br/>"
        "• <b>API</b> : FastAPI<br/>"
        "• <b>Base</b> : Supabase (PostgreSQL) free<br/>"
        "• <b>Hébergement API</b> : Render free (ou Tunnel Cloudflare le jour J)<br/>"
        "• <b>Auth</b> : JWT + PIN événement<br/>"
        "• <b>Sync</b> : bouton dans l’app PC existante",
        s["body"]
    ))
    story.append(Paragraph(
        "Vous n’avez pas besoin d’acheter un serveur, une licence de base de données, "
        "ni un SDK QR payant. Les seuls coûts éventuels sont la publication sur les stores "
        "et, plus tard, un hébergement payant si le free tier devient trop limité.",
        s["body"]
    ))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=BLEU_CLAIR))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Document généré pour le projet GestionInvitations — usage interne.",
        s["footer"]
    ))

    def first_page(canvas, doc):
        cover_page(canvas, doc)

    def later_pages(canvas, doc):
        header_footer(canvas, doc)

    # Build with cover as page 1 using onFirstPage, then content
    # Actually SimpleDocTemplate draws cover via onFirstPage but also flows story on same page.
    # Better: build cover-only first page by using a blank first flow + onFirstPage,
    # then PageBreak into content. Or use BaseDocTemplate. Simpler approach:
    # use onFirstPage for cover and start story with PageBreak.

    story_final = [PageBreak()] + story

    doc.build(story_final, onFirstPage=first_page, onLaterPages=later_pages)
    print(f"PDF créé : {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build()
