"""
Style visuel partagé + fonctions statistiques communes (percentile, z-score,
bandes de récession) utilisées par tous les graphiques.

L'idée : un seul fichier à modifier pour changer l'identité visuelle de
TOUS les graphiques du projet (couleurs, police, logo, etc.).
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# --- Palette -----------------------------------------------------------------
COLOR_ACCENT = "#1a3a5c"      # bleu marine sobre, couleur principale
COLOR_ACCENT_LIGHT = "#5b8ab8"
COLOR_GRID = "#e0e0e0"
COLOR_RECESSION = "#d0d0d0"
COLOR_TEXT = "#333333"

# Dates des récessions US (NBER), pour les bandes grisées en fond.
# À mettre à jour si besoin — source: NBER Business Cycle Dating Committee.
NBER_RECESSIONS = [
    ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]


def setup_figure(figsize=(10, 6)):
    """Crée une figure/axe avec le style de base du projet."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.grid(True, color=COLOR_GRID, linewidth=0.7, alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors=COLOR_TEXT, labelsize=9)
    return fig, ax


def add_recession_bands(ax, date_min=None, date_max=None):
    """Ajoute les bandes grisées de récession NBER en fond de graphique."""
    for start, end in NBER_RECESSIONS:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        if date_min is not None and end_dt < pd.to_datetime(date_min):
            continue
        if date_max is not None and start_dt > pd.to_datetime(date_max):
            continue
        ax.axvspan(start_dt, end_dt, color=COLOR_RECESSION, alpha=0.5, zorder=0)


def add_source_footer(fig, source_text: str):
    """Ajoute une mention de source en bas de la figure, petit texte gris."""
    fig.text(0.01, 0.01, source_text, fontsize=7.5, color="#888888", ha="left")


def format_date_axis(ax):
    """Formatte l'axe des dates : années seulement, une graduation par an."""
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# --- Fonctions statistiques ---------------------------------------------------

def compute_zscore(series: pd.Series) -> pd.Series:
    """Z-score de la série sur toute la fenêtre disponible."""
    return (series - series.mean()) / series.std()


def compute_percentile_rank(series: pd.Series) -> float:
    """Percentile de la dernière valeur par rapport à tout l'historique de la série."""
    last_value = series.iloc[-1]
    return float((series < last_value).mean() * 100)


def annotate_last_point_percentile(ax, x_last, y_last, series: pd.Series, years_label: str = "10 ans"):
    """Annote le dernier point du graphique avec son percentile historique."""
    pct = compute_percentile_rank(series)
    ax.annotate(
        f"Percentile {years_label}: {pct:.0f}e",
        xy=(x_last, y_last),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8.5,
        color=COLOR_ACCENT,
        fontweight="bold",
    )
