"""
Graphique : Pente de la courbe des taux US (2s10s et 3m10y)

Séries FRED :
  - T10Y2Y : écart 10 ans - 2 ans du Trésor US, quotidien, en points de %
  - T10Y3M : écart 10 ans - 3 mois du Trésor US, quotidien, en points de %

Ces deux séries sont des SPREADS déjà calculés et publiés par FRED (pas
besoin de soustraire deux séries de taux soi-même -- moins de code, moins
de risque d'erreur d'alignement).

Pourquoi c'est utile : l'inversion de la courbe des taux (spread négatif)
est l'indicateur avancé de récession le plus documenté de la littérature --
chaque récession US depuis les années 1960 a été précédée d'une inversion,
avec un délai typique de 6 à 24 mois. Le 3m10y est la variante préférée de
la recherche académique (Estrella & Mishkin) et de la Fed de New York ; le
2s10s est la variante la plus suivie par les marchés. Les afficher ensemble
évite de se raconter une histoire sur la base d'une seule des deux.

Complémentarité avec le chart 02 (Sahm Rule) : la courbe des taux est un
signal de MARCHÉ, en avance de plusieurs trimestres ; la Sahm Rule est un
signal d'EMPLOI, quasi coïncident. Courbe inversée + Sahm déclenchée =
faisceau d'indices convergent.

Sortie : PNG dans output/{periode}/17_yield_curve_slope.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

COLOR_3M10Y = "#c0392b"


def compute_curve_slopes(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, spread_2s10s, spread_3m10y.
    Les deux séries sont quotidiennes, publiées les mêmes jours ouvrés ->
    merge_asof avec petite tolérance par sécurité.
    """
    s2s10s = get_series("T10Y2Y", years=years)
    s3m10y = get_series("T10Y3M", years=years)

    s2s10s = s2s10s.rename(columns={"value": "spread_2s10s"}).sort_values("date")
    s3m10y = s3m10y.rename(columns={"value": "spread_3m10y"}).sort_values("date")

    merged = pd.merge_asof(s2s10s, s3m10y, on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=5))
    return merged.dropna(subset=["spread_2s10s"]).reset_index(drop=True)


def generate():
    df = compute_curve_slopes()

    if df.empty:
        raise RuntimeError(
            "[17_yield_curve_slope] Aucune donnée récupérée depuis FRED "
            "(T10Y2Y/T10Y3M). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["spread_2s10s"], color=COLOR_ACCENT, linewidth=1.6,
            label="10 ans - 2 ans (2s10s)", zorder=3)
    slope_3m = df.dropna(subset=["spread_3m10y"])
    if not slope_3m.empty:
        ax.plot(slope_3m["date"], slope_3m["spread_3m10y"], color=COLOR_3M10Y, linewidth=1.4,
                label="10 ans - 3 mois (3m10y)", zorder=2, alpha=0.85)

    # Ligne zéro : sous cette ligne, la courbe est inversée
    ax.axhline(0, color="#555555", linewidth=1.0, linestyle="--", zorder=1)

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Spread (points de %)", fontsize=9)
    ax.set_title("Pente de la courbe des taux US : 2s10s et 3m10y",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    # Dernier point du 2s10s (la variante la plus suivie par les marchés)
    ax.plot(last_row["date"], last_row["spread_2s10s"], marker="o", markersize=5,
            color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['spread_2s10s']:+.2f} pt",
        xy=(last_row["date"], last_row["spread_2s10s"]),
        xytext=(10, 0), textcoords="offset points",
        fontsize=8.5, color=COLOR_ACCENT, fontweight="bold", va="center",
    )

    add_source_footer(
        fig,
        "Source: FRED (T10Y2Y, T10Y3M) | Spread < 0 = courbe inversée, "
        "signal avancé de récession (délai historique 6-24 mois)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "17_yield_curve_slope.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[17_yield_curve_slope] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
