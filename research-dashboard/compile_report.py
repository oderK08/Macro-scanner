"""
Compile tous les graphiques générés (output/{periode}/*.png) en un seul
rapport PDF, façon note de recherche : page de garde, sommaire, puis 2
graphiques par page avec un commentaire analytique à côté de chacun.

Texte affiché à côté de chaque graphique :
  1. Le résumé statique tiré du README du graphique (toujours affiché)
  2. En dessous, s'il existe, le commentaire d'interprétation de la
     configuration actuelle généré via l'API Anthropic
     (output/{periode}/commentary.json -- voir generate_commentary.py)

Usage :
    python compile_report.py                # période courante (auto-détectée)
    python compile_report.py --period 2026S2 # période explicite

Ce script est indépendant de run_all.py et generate_commentary.py -- il se
contente de lire les PNG déjà générés et, s'il existe, le fichier
commentary.json. Un graphique sans PNG est simplement ignoré.
"""
import os
import re
import json
import argparse
from datetime import datetime

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle,
    KeepInFrame,
)
from reportlab.lib import colors
from PIL import Image as PILImage

from common.config import PROJECT_ROOT, OUTPUT_DIR, get_current_period_label
from common.themes import ordered_chart_dirs

CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")
PAGE_SIZE = landscape(letter)
MARGIN = 0.5 * inch
CHARTS_PER_PAGE = 2


def _discover_charts():
    """Retourne la liste triée des dossiers charts/NN_nom/."""
    entries = []
    for name in sorted(os.listdir(CHARTS_DIR)):
        path = os.path.join(CHARTS_DIR, name)
        if os.path.isdir(path) and re.match(r"^\d{2}_", name):
            entries.append(name)
    return entries


def _markdown_to_reportlab(text: str) -> str:
    """Convertit un minimum de markdown (gras, code inline) en balises reportlab."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    return text


def _extract_title_and_summary(readme_path: str):
    """
    Résumé de repli (utilisé si aucun commentaire API n'est disponible pour
    ce graphique) : titre + paragraphe "Pourquoi" du README.
    """
    if not os.path.exists(readme_path):
        return "Graphique", ""

    with open(readme_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.splitlines()
    title = "Graphique"
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    # Le numéro du graphique est déjà affiché dans sa propre colonne du
    # sommaire (préfixe du nom de dossier) : si un README garde un titre à
    # l'ancienne convention "NN — Titre", on retire le préfixe redondant.
    title = re.sub(r"^\d+\s*[—–-]\s*", "", title)

    summary_lines = []
    capturing = False
    for line in lines:
        if line.startswith("## "):
            if "pourquoi" in line.lower():
                capturing = True
                continue
            elif capturing:
                break
        if capturing and line.strip():
            summary_lines.append(line.strip())

    summary = " ".join(summary_lines).strip()
    if len(summary) > 600:
        summary = summary[:597].rsplit(" ", 1)[0] + "..."

    return title, _markdown_to_reportlab(summary)


def _fit_image(image_path: str, max_width: float, max_height: float) -> Image:
    """Redimensionne l'image pour tenir dans (max_width, max_height) en conservant le ratio."""
    with PILImage.open(image_path) as img:
        px_width, px_height = img.size
    ratio = min(max_width / px_width, max_height / px_height)
    return Image(image_path, width=px_width * ratio, height=px_height * ratio)


def build_report(period_label: str = None, output_path: str = None):
    if period_label is None:
        period_label = get_current_period_label()

    charts_output_dir = os.path.join(OUTPUT_DIR, period_label)
    if output_path is None:
        output_path = os.path.join(charts_output_dir, f"rapport_{period_label}.pdf")

    if not os.path.isdir(charts_output_dir):
        raise RuntimeError(
            f"[compile_report] Dossier introuvable: {charts_output_dir}. "
            "Lance d'abord run_all.py pour générer les graphiques de cette période."
        )

    commentary_path = os.path.join(charts_output_dir, "commentary.json")
    commentaries = {}
    if os.path.exists(commentary_path):
        with open(commentary_path, "r", encoding="utf-8") as f:
            commentaries = json.load(f)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=26, alignment=TA_CENTER, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"), spaceAfter=4,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=9.5, leading=13, alignment=TA_LEFT,
    )
    # Commentaire IA affiché sous le résumé du README : italique + filet de
    # couleur pour qu'on distingue d'un coup d'œil le texte statique de la
    # lecture du moment.
    commentary_label_style = ParagraphStyle(
        "CommentaryLabel", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#1a3a5c"), fontName="Helvetica-Bold",
        spaceBefore=8, spaceAfter=2,
    )
    commentary_style = ParagraphStyle(
        "Commentary", parent=body_style, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#333333"),
        borderColor=colors.HexColor("#1a3a5c"), borderWidth=0,
        leftIndent=6,
    )

    doc = SimpleDocTemplate(
        output_path, pagesize=PAGE_SIZE,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
    )
    story = []

    # --- Page de garde ---
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("Note de recherche macro & micro-économique", title_style))
    story.append(Paragraph(f"Période : {period_label}", subtitle_style))
    story.append(Paragraph(f"Édition du {datetime.today().strftime('%d/%m/%Y')}", subtitle_style))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "Sources : Federal Reserve Economic Data (FRED) et SEC EDGAR.",
        ParagraphStyle("CoverNote", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER,
                       textColor=colors.HexColor("#888888")),
    ))
    story.append(PageBreak())

    # --- Sommaire (groupé par thème) ---
    # L'ordre d'affichage (thèmes, puis graphiques au sein de chaque thème)
    # est piloté par common/themes.py -- les noms de dossiers charts/NN_*
    # restent inchangés, seul l'ordre de présentation dans le rapport change.
    chart_dirs = _discover_charts()
    themed_charts = ordered_chart_dirs(chart_dirs)

    toc_rows = []       # lignes du sommaire ; None en col 0 = ligne de thème
    chart_pages = []    # (theme, chart_dir, png_path, title, summary, commentary)

    # Métadonnées du fichier de commentaires (date de génération) : servent
    # au libellé au-dessus de chaque commentaire IA.
    commentary_meta = commentaries.get("_meta", {})
    commentary_label = "Lecture du moment — commentaire généré par IA"
    if isinstance(commentary_meta, dict) and commentary_meta.get("generated_at"):
        commentary_label += f" ({commentary_meta['generated_at']})"

    current_theme = None
    for theme, chart_dir in themed_charts:
        if theme != current_theme:
            toc_rows.append([None, theme, ""])
            current_theme = theme

        num_prefix = chart_dir[:2]
        png_candidates = [
            f for f in os.listdir(charts_output_dir)
            if f.startswith(num_prefix) and f.endswith(".png")
        ] if os.path.isdir(charts_output_dir) else []

        readme_path = os.path.join(CHARTS_DIR, chart_dir, "README.md")
        title, fallback_summary = _extract_title_and_summary(readme_path)

        if png_candidates:
            png_path = os.path.join(charts_output_dir, png_candidates[0])
            commentary = str(commentaries.get(chart_dir, "") or "").strip()
            # Pas de mention "Inclus" : être dans le sommaire suffit, seule
            # l'absence d'un graphique mérite une mention explicite.
            toc_rows.append([num_prefix, title, ""])
            chart_pages.append(
                (theme, chart_dir, png_path, title, fallback_summary, commentary)
            )
        else:
            toc_rows.append([num_prefix, title, "Non disponible cette période"])
            print(f"[compile_report] {chart_dir}: pas de PNG trouvé pour cette période, ignoré dans le rapport.")

    story.append(Paragraph("Sommaire", section_title_style))
    story.append(Spacer(1, 0.15 * inch))
    table_data = [
        ["" if row[0] is None else row[0], row[1], row[2]] for row in toc_rows
    ]
    table = Table(table_data, colWidths=[0.6 * inch, 6.5 * inch, 2.3 * inch])
    table_style = [
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i, row in enumerate(toc_rows):
        if row[0] is None:  # ligne de thème : gras, fond gris clair
            table_style += [
                ("FONTNAME", (0, i), (-1, i), "Helvetica-Bold"),
                ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f0f2f5")),
                ("TEXTCOLOR", (0, i), (-1, i), colors.HexColor("#1a3a5c")),
                ("TOPPADDING", (0, i), (-1, i), 8),
            ]
    table.setStyle(TableStyle(table_style))
    story.append(table)
    story.append(PageBreak())

    # --- Deux graphiques par page, texte à côté de chacun ---
    page_width, page_height = PAGE_SIZE
    usable_width = page_width - 2 * MARGIN
    usable_height = page_height - 2 * MARGIN

    unit_height = usable_height / CHARTS_PER_PAGE - 0.15 * inch
    image_col_width = usable_width * 0.60
    text_col_width = usable_width * 0.40
    # Plus de titre séparé au-dessus de chaque image (chaque PNG porte déjà
    # son propre titre) : la hauteur libérée revient à l'image.
    image_max_height = (unit_height - 0.10 * inch) * 0.95

    def _build_unit(chart_dir, png_path, summary, commentary, max_image_height=None):
        if max_image_height is None:
            max_image_height = image_max_height
        # Pas de titre reportlab au-dessus de l'image : chaque PNG contient
        # déjà son titre (ax.set_title) -- l'afficher deux fois créait un
        # doublon typographique lourd sur chaque page. Le titre extrait des
        # README ne sert plus qu'au sommaire.
        image_flowable = _fit_image(png_path, image_col_width - 0.1 * inch, max_image_height)
        left_cell = [image_flowable]

        # Résumé statique du README, puis en dessous le commentaire IA de la
        # configuration actuelle (s'il existe pour ce graphique).
        text_flowables = []
        if summary:
            text_flowables.append(Paragraph(summary, body_style))
        if commentary:
            text_flowables.append(Paragraph(commentary_label, commentary_label_style))
            text_flowables.append(Paragraph(commentary, commentary_style))
        if not text_flowables:
            text_flowables = [Spacer(1, 1)]
        # KeepInFrame en mode "shrink" : si résumé + commentaire dépassent la
        # hauteur allouée, le bloc de texte est réduit pour tenir -- le
        # rapport reste lisible quelle que soit la longueur des textes,
        # aucune maintenance de mise en page à prévoir.
        right_cell = [KeepInFrame(
            text_col_width - 14, max_image_height, text_flowables, mode="shrink"
        )]

        unit_table = Table(
            [[left_cell, right_cell]],
            colWidths=[image_col_width, text_col_width],
        )
        unit_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("LEFTPADDING", (1, 0), (1, 0), 14),
            ("RIGHTPADDING", (0, 0), (0, 0), 4),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ]))
        return unit_table

    # Regroupement par thème : chaque thème démarre sur une nouvelle page
    # avec un bandeau de section, puis 2 graphiques par page au sein du thème.
    theme_banner_style = ParagraphStyle(
        "ThemeBanner", parent=styles["Heading1"], fontSize=15,
        textColor=colors.HexColor("#1a3a5c"), spaceAfter=10,
    )

    # Hauteur consommée par le bandeau de thème (police 15 + interlignage +
    # espacements du style Heading1) : à retrancher de la hauteur d'image des
    # graphiques partageant la première page d'un thème, sinon le 2e graphique
    # déborde sur une page supplémentaire.
    banner_height = 0.55 * inch

    themes_in_order = []
    for entry in chart_pages:
        if entry[0] not in themes_in_order:
            themes_in_order.append(entry[0])

    for theme in themes_in_order:
        theme_entries = [e for e in chart_pages if e[0] == theme]
        for i in range(0, len(theme_entries), CHARTS_PER_PAGE):
            batch = theme_entries[i:i + CHARTS_PER_PAGE]
            is_banner_page = (i == 0)
            if is_banner_page:
                story.append(Paragraph(theme, theme_banner_style))
            unit_image_height = (
                image_max_height - banner_height / CHARTS_PER_PAGE
                if is_banner_page else image_max_height
            )
            for j, (_theme, chart_dir, png_path, _title, summary, commentary) in enumerate(batch):
                story.append(_build_unit(chart_dir, png_path, summary, commentary,
                                         max_image_height=unit_image_height))
                if j < len(batch) - 1:
                    story.append(Spacer(1, 0.15 * inch))
            story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()  # éviter une dernière page blanche

    doc.build(story)
    n_with_analysis = sum(1 for c in chart_pages if c[5])
    print(
        f"[compile_report] Rapport PDF généré: {output_path} "
        f"({len(chart_pages)} graphiques, {n_with_analysis} avec commentaire analytique)"
    )
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile les graphiques générés en un rapport PDF.")
    parser.add_argument("--period", default=None, help="Période à compiler, ex: 2026S2 (défaut: période courante)")
    args = parser.parse_args()
    build_report(period_label=args.period)
