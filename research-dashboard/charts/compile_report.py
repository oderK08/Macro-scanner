"""
Compile tous les graphiques générés (output/{periode}/*.png) en un seul
rapport PDF, façon note de recherche : page de garde, sommaire, puis une
page par graphique avec son titre et un court résumé tiré du README de
chaque chart.

Usage :
    python compile_report.py                # période courante (auto-détectée)
    python compile_report.py --period 2026S2 # période explicite

Ce script est indépendant de run_all.py -- il se contente de lire les PNG
déjà générés dans output/{periode}/ et les README.md dans charts/*/.
Si un graphique n'a pas encore de PNG (stub pas encore implémenté, ou run
partiel), il est simplement ignoré, avec un message, plutôt que de faire
planter toute la compilation.
"""
import os
import re
import sys
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
MARGIN = 0.6 * inch


def _discover_charts():
    """
    Retourne la liste triée des dossiers charts/NN_nom/, avec leur numéro.
    """
    entries = []
    for name in sorted(os.listdir(CHARTS_DIR)):
        path = os.path.join(CHARTS_DIR, name)
        if os.path.isdir(path) and re.match(r"^\d{2}_", name):
            entries.append(name)
    return entries


def _markdown_to_reportlab(text: str) -> str:
    """
    Convertit un minimum de syntaxe markdown (gras, code inline) en balises
    que reportlab sait interpréter dans un Paragraph. Sans ça, "**mot**"
    s'affiche avec les astérisques littéraux au lieu d'être mis en gras.
    """
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    return text


def _extract_title_and_summary(readme_path: str):
    """
    Extrait un titre (première ligne '# ...') et un court résumé (le
    paragraphe sous une section dont le titre contient 'Pourquoi') depuis un
    README.md de chart. Retourne (title, summary), avec des valeurs de repli
    si le README est absent ou ne suit pas le format attendu.
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
    # Un résumé de README peut être long ; on le limite pour qu'il tienne
    # confortablement sous le graphique sans déborder de la page.
    if len(summary) > 500:
        summary = summary[:497].rsplit(" ", 1)[0] + "..."

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

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=26, alignment=TA_CENTER, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=13, alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"), spaceAfter=4,
    )
    chart_title_style = ParagraphStyle(
        "ChartTitle", parent=styles["Heading1"], fontSize=16, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_LEFT,
    )
    toc_entry_style = ParagraphStyle(
        "TocEntry", parent=styles["Normal"], fontSize=11, leading=18,
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
    story.append(Paragraph(f"Généré automatiquement le {datetime.today().strftime('%d/%m/%Y')}", subtitle_style))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "Sources : Federal Reserve Economic Data (FRED) et SEC EDGAR. "
        "Voir le README de chaque graphique dans le dépôt pour le détail des séries, "
        "du calcul et des limitations.",
        ParagraphStyle("CoverNote", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER,
                       textColor=colors.HexColor("#888888")),
    ))
    story.append(PageBreak())

    # --- Sommaire ---
    chart_dirs = _discover_charts()
    toc_rows = []
    chart_pages = []  # (chart_dir, png_path, title, summary)

    for chart_dir in chart_dirs:
        num_prefix = chart_dir[:2]
        png_candidates = [
            f for f in os.listdir(charts_output_dir)
            if f.startswith(num_prefix) and f.endswith(".png")
        ] if os.path.isdir(charts_output_dir) else []

        readme_path = os.path.join(CHARTS_DIR, chart_dir, "README.md")
        title, summary = _extract_title_and_summary(readme_path)

        if png_candidates:
            png_path = os.path.join(charts_output_dir, png_candidates[0])
            toc_rows.append([num_prefix, title, "Inclus"])
            chart_pages.append((chart_dir, png_path, title, summary))
        else:
            toc_rows.append([num_prefix, title, "Non disponible ce trimestre"])
            print(f"[compile_report] {chart_dir}: pas de PNG trouvé pour cette période, ignoré dans le rapport.")

    story.append(Paragraph("Sommaire", chart_title_style))
    story.append(Spacer(1, 0.15 * inch))
    table = Table(toc_rows, colWidths=[0.6 * inch, 5.5 * inch, 2.3 * inch])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(PageBreak())

    # --- Une page par graphique disponible ---
    page_width, page_height = PAGE_SIZE
    available_width = page_width - 2 * MARGIN
    available_height_for_image = page_height - 2 * MARGIN - 1.6 * inch  # place pour titre + résumé

    for chart_dir, png_path, title, summary in chart_pages:
        story.append(Paragraph(title, chart_title_style))
        story.append(_fit_image(png_path, available_width, available_height_for_image))
        if summary:
            story.append(Spacer(1, 0.12 * inch))
            story.append(Paragraph(summary, body_style))
        story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()  # éviter une dernière page blanche à la fin

    doc.build(story)
    print(f"[compile_report] Rapport PDF généré: {output_path} ({len(chart_pages)} graphiques inclus)")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile les graphiques générés en un rapport PDF.")
    parser.add_argument("--period", default=None, help="Période à compiler, ex: 2026S2 (défaut: période courante)")
    args = parser.parse_args()
    build_report(period_label=args.period)
