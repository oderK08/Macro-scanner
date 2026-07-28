"""
Compile tous les graphiques générés (output/{periode}/*.png) en un seul
rapport PDF, façon note de recherche : page de garde, sommaire, puis 2
graphiques par page avec un commentaire analytique à côté de chacun.

Priorité du texte affiché à côté de chaque graphique :
  1. Le commentaire généré via l'API Anthropic (output/{periode}/commentary.json),
     s'il existe pour ce graphique -- voir generate_commentary.py
  2. À défaut, le résumé statique tiré du README du graphique

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
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
)
from reportlab.lib import colors
from PIL import Image as PILImage

from common.config import PROJECT_ROOT, OUTPUT_DIR, get_current_period_label

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
    chart_title_style = ParagraphStyle(
        "ChartTitle", parent=styles["Heading2"], fontSize=12, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=9.5, leading=13, alignment=TA_LEFT,
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

    # --- Sommaire ---
    chart_dirs = _discover_charts()
    toc_rows = []
    chart_pages = []  # (chart_dir, png_path, title, text)

    for chart_dir in chart_dirs:
        num_prefix = chart_dir[:2]
        png_candidates = [
            f for f in os.listdir(charts_output_dir)
            if f.startswith(num_prefix) and f.endswith(".png")
        ] if os.path.isdir(charts_output_dir) else []

        readme_path = os.path.join(CHARTS_DIR, chart_dir, "README.md")
        title, fallback_summary = _extract_title_and_summary(readme_path)

        if png_candidates:
            png_path = os.path.join(charts_output_dir, png_candidates[0])
            analysis_text = commentaries.get(chart_dir, "").strip()
            text = analysis_text if analysis_text else fallback_summary
            toc_rows.append([num_prefix, title, "Inclus"])
            chart_pages.append((chart_dir, png_path, title, text))
        else:
            toc_rows.append([num_prefix, title, "Non disponible ce trimestre"])
            print(f"[compile_report] {chart_dir}: pas de PNG trouvé pour cette période, ignoré dans le rapport.")

    story.append(Paragraph("Sommaire", section_title_style))
    story.append(Spacer(1, 0.15 * inch))
    table = Table(toc_rows, colWidths=[0.6 * inch, 6.5 * inch, 2.3 * inch])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(PageBreak())

    # --- Deux graphiques par page, texte à côté de chacun ---
    page_width, page_height = PAGE_SIZE
    usable_width = page_width - 2 * MARGIN
    usable_height = page_height - 2 * MARGIN

    unit_height = usable_height / CHARTS_PER_PAGE - 0.15 * inch
    image_col_width = usable_width * 0.60
    text_col_width = usable_width * 0.40
    image_max_height = (unit_height - 0.35 * inch) * 0.92  # marge de sécurité (paddings, interlignage)

    def _build_unit(chart_dir, png_path, title, text):
        image_flowable = _fit_image(png_path, image_col_width - 0.1 * inch, image_max_height)
        left_cell = [Paragraph(title, chart_title_style), image_flowable]
        right_cell = [Paragraph(text, body_style)] if text else [Spacer(1, 1)]

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

    for i in range(0, len(chart_pages), CHARTS_PER_PAGE):
        batch = chart_pages[i:i + CHARTS_PER_PAGE]
        for j, (chart_dir, png_path, title, text) in enumerate(batch):
            story.append(_build_unit(chart_dir, png_path, title, text))
            if j < len(batch) - 1:
                story.append(Spacer(1, 0.15 * inch))
        story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()  # éviter une dernière page blanche

    doc.build(story)
    n_with_analysis = sum(1 for c in chart_pages if commentaries.get(c[0], "").strip())
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
