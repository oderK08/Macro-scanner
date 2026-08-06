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

# Le projet n'utilise jamais la notation mathématique de matplotlib, mais
# ses labels contiennent souvent des montants avec "$" (ex: "5.70 T$") --
# sans ceci, une PAIRE de "$" dans un même texte (ex: un label de légende
# "($T, éch. gauche) : 5.70 T$") bascule silencieusement le texte entre les
# deux en italique mathématique. Désactivé globalement, une fois pour toutes.
plt.rcParams["text.parse_math"] = False

# --- Palette sémantique -------------------------------------------------------
# UNE seule convention de couleurs pour tout le projet, par RÔLE de série --
# jamais de couleur ad hoc dans un generate.py. Le lecteur du rapport apprend
# la convention une fois et la retrouve sur chaque graphique :
#   - série principale        -> COLOR_ACCENT (bleu marine, trait plein)
#   - deuxième série          -> COLOR_SECOND (rouge brique)
#   - troisième série         -> COLOR_THIRD (bleu clair)
#   - série de référence/contexte (ex: S&P 500 en superposition, taux
#     nominal derrière un taux réel) -> COLOR_BENCHMARK (gris, pointillés)
#   - seuils/lignes d'alerte  -> COLOR_SECOND en pointillés
#   - palettes catégorielles (11 secteurs GICS, tickers, pays) -> tab20,
#     indexée par ordre alphabétique (voir _sector_color_map des charts 11/12/23)
COLOR_ACCENT = "#1a3a5c"      # bleu marine sobre, série principale
COLOR_SECOND = "#c0392b"      # rouge brique, deuxième série / seuils d'alerte
COLOR_THIRD = "#8fb8d8"       # bleu clair, troisième série
COLOR_BENCHMARK = "#aaaaaa"   # gris, série de référence/contexte (pointillés)
COLOR_ACCENT_LIGHT = "#5b8ab8"
COLOR_GRID = "#e0e0e0"
COLOR_RECESSION = "#d0d0d0"
COLOR_TEXT = "#333333"

# --- Géométrie unique ---------------------------------------------------------
# Tous les graphiques du projet partagent exactement la même taille de figure
# ET les mêmes marges (pas de tight_layout, qui ajuste les marges au contenu
# et donne des zones de tracé de tailles légèrement différentes d'un chart à
# l'autre). Résultat : chaque PNG a la zone de tracé au même endroit, à la
# même taille -- alignement parfait dans le rapport PDF.
FIGSIZE = (10, 6.3)
SAVE_DPI = 150
# Marges figure (fractions) : la bande du bas accueille les étiquettes de
# l'axe X, puis la légende (toujours SOUS le graphique, jamais dans la zone
# de tracé), puis le footer de source.
_MARGINS = dict(left=0.08, right=0.92, top=0.87, bottom=0.22)
# Ancre verticale de la légende, en fraction d'axes sous l'axe X
# (l'espace [axe X -> bas de figure] fait 0.22 de la figure : étiquettes de
# dates ~0.04, légende ~0.10, footer le reste).
_LEGEND_Y_ANCHOR = -0.10

# Dates des récessions US (NBER), pour les bandes grisées en fond.
# À mettre à jour si besoin — source: NBER Business Cycle Dating Committee.
NBER_RECESSIONS = [
    ("1990-07-01", "1991-03-01"),
    ("2001-03-01", "2001-11-01"),
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]


def setup_figure():
    """
    Crée une figure/axe avec le style de base du projet. La taille est
    volontairement NON paramétrable : tous les graphiques du rapport doivent
    avoir exactement la même géométrie (voir FIGSIZE/_MARGINS ci-dessus).
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
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
    Ajoute une mention de source en bas de la figure, petit texte gris.
    Le texte est automatiquement replié sur plusieurs lignes s'il est trop
    long pour la largeur de la figure -- jamais tronqué à droite, quelle
    que soit la longueur du texte de source d'un chart.
    """
    import textwrap
    text = source_text
    if as_of_date is not None:
        date_str = pd.to_datetime(as_of_date).strftime("%d/%m/%Y")
        text = f"{source_text} | Données au {date_str}"
    # ~155 caractères tiennent sur la largeur utile en fontsize 7.5
    wrapped = "\n".join(textwrap.wrap(text, width=155))
    fig.text(0.02, 0.005, wrapped, fontsize=7.5, color="#888888", ha="left", va="bottom")


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


def mark_last_point(ax, x_last, y_last, color=None):
    """
    Marque le dernier point d'une série d'un point plein -- SANS texte.

    Règle du projet : AUCUN texte dans la zone de tracé. La valeur du
    dernier point (et son percentile) vont dans le label de légende de la
    série (voir format_last_value_label), la légende étant rendue sous le
    graphique par finalize_chart. Un texte posé au bout d'une courbe finit
    toujours par chevaucher une autre courbe ou un axe pour certaines
    valeurs de données -- impossible à garantir sur un projet qui doit
    tourner des années sans intervention manuelle.
    """
    if color is None:
        color = COLOR_ACCENT
    ax.plot(x_last, y_last, marker="o", markersize=5, color=color, zorder=5)


def format_last_value_label(name: str, value_str: str, series: pd.Series = None,
                            years_label: str = None) -> str:
    """
    Construit un label de légende enrichi de la dernière valeur, et
    optionnellement du percentile historique de la série :
        "Taux réel : 1.2% (78e pct 10 ans)"
    C'est le remplaçant des anciennes annotations au bout des courbes.
    """
    label = f"{name} : {value_str}"
    if series is not None:
        pct = compute_percentile_rank(series)
        suffix = f" {years_label}" if years_label else ""
        label += f" ({pct:.0f}e pct{suffix})"
    return label


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


def finalize_chart(fig, ax, out_path: str, handles=None, labels=None,
                   legend_ncol: int = 2, note: str = None):
    """
    Étape finale unique de TOUS les graphiques du projet :
      - légende horizontale SOUS la zone de tracé (jamais dedans -- elle ne
        peut donc jamais masquer de données, quelles que soient les valeurs
        futures des séries)
      - note optionnelle (repère hors échelle, chiffre-clé...) rendue dans
        la même bande basse, alignée à droite -- même garantie
      - marges FIXES identiques pour tous les charts (pas de tight_layout) :
        chaque PNG a sa zone de tracé exactement au même endroit et à la
        même taille
      - sauvegarde + fermeture de la figure

    handles/labels : à passer explicitement pour les charts à deux axes
    (twinx), où les lignes vivent sur deux axes différents. Par défaut,
    reprend les handles de `ax`.
    """
    if handles is None:
        handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(
            handles, labels if labels is not None else [h.get_label() for h in handles],
            loc="upper left", bbox_to_anchor=(0.0, _LEGEND_Y_ANCHOR),
            ncol=legend_ncol, fontsize=8.5, frameon=False, borderaxespad=0,
            columnspacing=1.3, handlelength=1.6, handletextpad=0.5,
        )
    if note:
        fig.text(_MARGINS["right"], 0.075, note, fontsize=8, ha="right",
                 va="bottom", style="italic", color="#666666")

    fig.subplots_adjust(**_MARGINS)
    fig.savefig(out_path, dpi=SAVE_DPI)
    plt.close(fig)
    return out_path
