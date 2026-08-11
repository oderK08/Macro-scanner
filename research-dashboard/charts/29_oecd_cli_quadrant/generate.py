"""
Graphique : Quadrant de momentum du cycle mondial (OECD Composite Leading
Indicators) -- niveau vs variation 3 mois, un point par économie.

Source : DBnomics (https://db.nomics.world), qui republie les Composite
Leading Indicators de l'OCDE en JSON simple, sans clé API. Le CLI est
construit par l'OCDE précisément pour anticiper les points de retournement
du cycle 6 à 9 mois à l'avance ; 100 = tendance de long terme de
l'activité.

⚠️ Source non éprouvée en conditions réelles au moment de l'écriture
(domaine inaccessible depuis l'environnement de développement) : premier
run à valider, comme les charts 15/27. L'OCDE a réorganisé ses jeux de
données en 2023-2024 -- ce script essaie plusieurs identifiants de dataset
candidats, du plus récent au plus ancien, et cherche les séries par texte
libre plutôt que par code figé, pour survivre à ces réorganisations.

Lecture du quadrant (style "notes de banque") :
  haut-droit  = au-dessus de la tendance ET en accélération
  haut-gauche = au-dessus de la tendance mais en décélération
  bas-gauche  = sous la tendance et en décélération
  bas-droit   = sous la tendance mais en amélioration (début de reprise)
La traîne de 6 mois derrière chaque point montre d'où vient chaque
économie -- le sens de rotation habituel est anti-horaire.

Sortie : PNG dans output/{periode}/29_oecd_cli_quadrant.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.dbnomics_client import search_series, get_series_observations
from common.chart_style import (
    setup_figure, add_source_footer, add_freshness_subtitle, finalize_chart,
    COLOR_GRID,
)
from common.config import get_current_period_label, OUTPUT_DIR

PROVIDER = "OECD"
# Identifiants de dataset candidats, essayés dans l'ordre : l'OCDE a migré
# ses CLI de MEI_CLI vers la nouvelle infrastructure (identifiants DSD_*)
# en 2023-2024, et DBnomics suit ces migrations avec un peu de latence.
DATASET_CANDIDATES = ["DSD_STES@DF_CLI", "MEI_CLI"]

# Économies suivies : nom d'affichage -> termes de recherche anglais.
COUNTRIES = {
    "États-Unis": "United States",
    "Zone euro": "Euro area",
    "Japon": "Japan",
    "Royaume-Uni": "United Kingdom",
    "Chine": "China",
}

MOMENTUM_MONTHS = 3   # variation sur 3 mois (axe X), comme les quadrants PMI
TRAIL_MONTHS = 6      # longueur de la traîne derrière chaque point

# Garde-fou : le CLI est un indice normalisé autour de 100 -- une valeur
# hors de cette plage signale une série mal identifiée (mauvaise unité,
# mauvais concept), pas un état extrême de l'économie.
CLI_PLAUSIBLE_RANGE = (70, 130)

COUNTRY_COLORS = ["#1a3a5c", "#c0392b", "#2f6690", "#e08e79", "#5b8ab8"]


def _find_cli_series(dataset: str, country_en: str):
    """
    Cherche la série CLI mensuelle ajustée d'amplitude pour un pays donné.
    Retourne (series_code, series_name) ou (None, None).
    """
    query = f"composite leading indicator amplitude adjusted {country_en}"
    docs = search_series(PROVIDER, dataset, query, limit=30)

    for doc in docs:
        code = doc.get("series_code", "")
        name = doc.get("series_name", "")
        name_l = name.lower()
        mentions_country = country_en.lower() in name_l
        mentions_amplitude = "amplitude" in name_l
        if mentions_country and mentions_amplitude:
            return code, name
    return None, None


def compute_cli_data() -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, country, value (CLI mensuel), limité
    aux TRAIL_MONTHS + MOMENTUM_MONTHS + 1 derniers mois par pays (le
    quadrant n'a pas besoin de plus d'historique).
    """
    records = []
    for display_name, country_en in COUNTRIES.items():
        series_df, found = None, None
        for dataset in DATASET_CANDIDATES:
            try:
                code, name = _find_cli_series(dataset, country_en)
                if code is None:
                    continue
                obs = get_series_observations(PROVIDER, dataset, code)
                if len(obs) < MOMENTUM_MONTHS + 2:
                    continue
                series_df, found = obs, (dataset, code)
                break
            except Exception as e:
                print(f"  [avertissement] {display_name} via {dataset}: {e} -- dataset suivant")
                continue

        if series_df is None:
            print(f"  [avertissement] {display_name}: aucune série CLI trouvée -- ignoré")
            continue

        series_df = series_df.sort_values("date").tail(TRAIL_MONTHS + MOMENTUM_MONTHS + 1)
        for _, row in series_df.iterrows():
            records.append({"date": row["date"], "country": display_name,
                            "value": float(row["value"])})
        print(f"[29_oecd_cli_quadrant] {display_name}: OK via {found[0]} ({found[1]})")

    return pd.DataFrame(records)


def generate():
    df = compute_cli_data()

    if df.empty:
        raise RuntimeError(
            "[29_oecd_cli_quadrant] Aucune série CLI récupérée depuis DBnomics pour "
            "aucun pays. Vérifie la connectivité vers api.db.nomics.world ; si le "
            "problème persiste, les identifiants de dataset OCDE ont probablement "
            "encore changé (voir DATASET_CANDIDATES en tête de fichier)."
        )

    fig, ax = setup_figure()
    handles = []
    last_dates = []

    for i, country in enumerate(COUNTRIES):
        sub = df[df["country"] == country].sort_values("date")
        if len(sub) < MOMENTUM_MONTHS + 1:
            continue

        values = sub["value"].reset_index(drop=True)
        momentum = values - values.shift(MOMENTUM_MONTHS)
        trail = pd.DataFrame({"level": values, "chg": momentum}).dropna().tail(TRAIL_MONTHS)
        if trail.empty:
            continue

        last_level = trail["level"].iloc[-1]
        last_chg = trail["chg"].iloc[-1]
        lo, hi = CLI_PLAUSIBLE_RANGE
        if not (lo <= last_level <= hi):
            raise RuntimeError(
                f"[29_oecd_cli_quadrant] CLI implausible pour {country}: {last_level:.1f} "
                f"(attendu dans [{lo}, {hi}]). La série récupérée n'est probablement pas "
                "le CLI ajusté d'amplitude -- schéma de données OCDE à re-vérifier."
            )

        color = COUNTRY_COLORS[i % len(COUNTRY_COLORS)]
        # Traîne des 6 derniers mois : ligne fine + petits points estompés.
        ax.plot(trail["chg"], trail["level"], color=color, linewidth=1.0,
                alpha=0.35, zorder=2)
        ax.plot(trail["chg"].iloc[:-1], trail["level"].iloc[:-1], linestyle="none",
                marker="o", markersize=3, color=color, alpha=0.35, zorder=2)
        # Point actuel : gros marqueur plein.
        handle, = ax.plot(last_chg, last_level, linestyle="none", marker="o",
                          markersize=11, color=color, zorder=4,
                          label=f"{country} : {last_level:.1f} | 3 mois {last_chg:+.2f}")
        handles.append(handle)
        last_dates.append(sub["date"].max())

    if not handles:
        raise RuntimeError(
            "[29_oecd_cli_quadrant] Aucun pays n'a assez d'historique pour calculer "
            "le momentum 3 mois -- données DBnomics incomplètes."
        )

    # Croix du quadrant : tendance (y=100) et momentum nul (x=0).
    ax.axhline(100, color="#999999", linewidth=1.0, linestyle="--", zorder=1)
    ax.axvline(0, color="#999999", linewidth=1.0, linestyle="--", zorder=1)

    # Échelle symétrique en X pour que le quadrant soit visuellement honnête
    # (0 au centre), avec un minimum de +/-0.5 point pour ne pas zoomer à
    # l'excès quand tous les momenta sont faibles.
    x_extent = max(0.5, abs(ax.get_xlim()[0]), abs(ax.get_xlim()[1]))
    ax.set_xlim(-x_extent, x_extent)

    ax.set_xlabel(f"Variation sur {MOMENTUM_MONTHS} mois (points d'indice)", fontsize=9)
    ax.set_ylabel("Niveau du CLI (100 = tendance de long terme)", fontsize=9)
    ax.set_title("Cycle mondial : indicateurs avancés OCDE, niveau vs momentum",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")

    last_date = max(last_dates)
    add_freshness_subtitle(ax, last_date)

    add_source_footer(
        fig,
        "Source: DBnomics (OECD, Composite Leading Indicators, ajustés d'amplitude) | "
        "Traîne = 6 derniers mois, rotation habituelle anti-horaire",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "29_oecd_cli_quadrant.png")

    finalize_chart(
        fig, ax, out_path, handles=handles, legend_ncol=3,
        note="Haut-droit : > tendance, en accélération | Bas-droit : < tendance, en amélioration",
    )

    print(f"[29_oecd_cli_quadrant] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
