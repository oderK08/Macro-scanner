"""
Style visuel partagé + fonctions statistiques communes (percentile, z-score,
bandes de récession) utilisées par tous les graphiques.

L'idée : un seul fichier à modifier pour changer l'identité visuelle de
TOUS les graphiques du projet (couleurs, police, logo, etc.).
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms as transforms
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


def add_recession_bands(ax, date_min=None, date_max=None, label_first=True):
    """
    Ajoute les bandes grisées de récession NBER en fond de graphique.
    Si label_first=True, ajoute un petit label discret sur la première bande
    visible pour que le lecteur comprenne ce que représente le gris.

    Important : le label utilise un transform "mixte" (x en coordonnées de
    données, y en fraction des axes) plutôt que l'échelle Y réelle. Ça le
    rend indépendant du moment où cette fonction est appelée par rapport à
    ax.plot() -- avant, l'échelle Y n'est pas encore définie par les vraies
    données (matplotlib utilise 0-1 par défaut), et un positionnement basé
    sur ylim() à ce stade placerait le label n'importe où une fois les
    vraies données tracées.
    """
    first_labeled = False
    for start, end in NBER_RECESSIONS:
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        if date_min is not None and end_dt < pd.to_datetime(date_min):
            continue
        if date_max is not None and start_dt > pd.to_datetime(date_max):
            continue
        ax.axvspan(start_dt, end_dt, color=COLOR_RECESSION, alpha=0.5, zorder=0)

        if label_first and not first_labeled:
            blended_transform = transforms.blended_transform_factory(ax.transData, ax.transAxes)
            ax.text(
                start_dt, 0.97, " Récession", fontsize=7, color="#999999",
                ha="left", va="top", style="italic",
                transform=blended_transform,
            )
            first_labeled = True


def add_source_footer(fig, source_text: str, as_of_date=None):
    """
    Ajoute une mention de source en bas de la figure, petit texte gris,
    avec assez de marge pour ne jamais être coupée.
    """
    text = source_text
    if as_of_date is not None:
        date_str = pd.to_datetime(as_of_date).strftime("%d/%m/%Y")
        text = f"{source_text} | Données au {date_str}"
    fig.text(0.02, 0.015, text, fontsize=7.5, color="#888888", ha="left")


def format_date_axis(ax, tight_to_last_point=None):
    """
    Formatte l'axe des dates : années seulement, une graduation par an.
    Si tight_to_last_point est fourni (date de dernier point réel), resserre
    l'axe X pour éviter le grand espace blanc à droite des charts.
    """
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    if tight_to_last_point is not None:
        current_min, _ = ax.get_xlim()
        margin = pd.Timedelta(days=60)
        new_max = mdates.date2num(pd.to_datetime(tight_to_last_point) + margin)
        ax.set_xlim(current_min, new_max)


def highlight_last_point(ax, x_last, y_last, value_label: str, color=None, offset=(8, 0)):
    """
    Marque visuellement le dernier point d'une série (point plein + valeur
    affichée juste à côté), pour que l'œil trouve immédiatement où s'arrête
    la courbe — pratique standard des charts de recherche.

    offset=(dx, dy) : décalage en points de l'étiquette par rapport au point.
    Augmente dy si l'étiquette chevauche une ligne ou la légende sur un
    graphique donné (à ajuster à la main, cas par cas, directement dans le
    generate.py concerné -- ne change rien pour les autres graphiques).
    """
    if color is None:
        color = COLOR_ACCENT
    ax.plot(x_last, y_last, marker="o", markersize=5, color=color, zorder=5)
    ax.annotate(
        value_label,
        xy=(x_last, y_last),
        xytext=offset,
        textcoords="offset points",
        fontsize=9,
        color=color,
        fontweight="bold",
        va="center",
    )


def add_freshness_subtitle(ax, as_of_date):
    """Ajoute une petite ligne 'Données au JJ/MM/AAAA' sous le titre."""
    date_str = pd.to_datetime(as_of_date).strftime("%d/%m/%Y")
    ax.text(
        0.0, 1.09, f"Données au {date_str}",
        transform=ax.transAxes, fontsize=8.5, color="#888888", ha="left",
    )


# --- Fonctions statistiques ---------------------------------------------------

def compute_zscore(series: pd.Series) -> pd.Series:
    """Z-score de la série sur toute la fenêtre disponible."""
    return (series - series.mean()) / series.std()


def compute_percentile_rank(series: pd.Series) -> float:
    """Percentile de la dernière valeur par rapport à tout l'historique de la série."""
    last_value = series.iloc[-1]
    return float((series < last_value).mean() * 100)


def annotate_last_point_percentile(ax, x_last, y_last, series: pd.Series, years_label: str = "10 ans",
                                     value_label: str = None, offset=(10, 0)):
    """
    Marque le dernier point (point plein) et affiche juste à côté la valeur
    actuelle + son percentile historique, sur deux lignes, bien accroché au
    point (pas flottant dans le vide comme avant).

    offset=(dx, dy) : décalage en points de l'étiquette par rapport au point.
    À ajuster à la main dans le generate.py concerné si l'étiquette chevauche
    autre chose sur un graphique précis (ex: offset=(10, 25) pour la
    remonter, offset=(-90, 15) pour la mettre à gauche du point plutôt qu'à
    droite).
    """
    pct = compute_percentile_rank(series)
    ax.plot(x_last, y_last, marker="o", markersize=5, color=COLOR_ACCENT, zorder=5)

    lines = []
    if value_label is not None:
        lines.append(value_label)
    lines.append(f"Percentile {years_label}: {pct:.0f}e")

    ax.annotate(
        "\n".join(lines),
        xy=(x_last, y_last),
        xytext=offset,
        textcoords="offset points",
        fontsize=8.5,
        color=COLOR_ACCENT,
        fontweight="bold",
        va="center",
    )
