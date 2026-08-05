"""
Graphique : Dollar pondéré par les échanges vs taux 10 ans US

Séries FRED :
  - DTWEXBGS : indice dollar large pondéré par les échanges (Fed Board,
               base janvier 2006 = 100), quotidien
  - DGS10    : rendement nominal du Trésor US 10 ans, quotidien, %

Choix de DTWEXBGS plutôt que le DXY : le DXY (ICE) est un indice
propriétaire sur-pondéré en euro (~58%), non disponible sur FRED. DTWEXBGS
est l'indice OFFICIEL de la Fed, pondéré par les échanges commerciaux réels
(incluant Chine, Mexique...), publié par une source publique stable -- le
bon choix pour un projet qui doit tourner sans maintenance pendant des
années.

Pourquoi c'est utile : le cycle du dollar est un des grands régimes macro
pour l'allocation globale. Un dollar fort resserre les conditions
financières mondiales (dette émergente en dollars, matières premières
libellées en dollars) et pèse mécaniquement sur les bénéfices étrangers des
multinationales US (~40% des revenus du S&P 500). Le taux 10 ans est
superposé car le différentiel de taux est le principal moteur du dollar --
quand les deux divergent (dollar qui baisse malgré des taux qui montent),
c'est le signal le plus intéressant du chart : le marché price un doute
sur le statut de valeur refuge des actifs US.

Sortie : PNG dans output/{periode}/20_dollar_index_vs_10y_yield.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, compute_percentile_rank, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

COLOR_YIELD = "#888888"


def compute_dollar_vs_yield(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, dollar_index, yield_10y.
    Deux séries quotidiennes (jours ouvrés) -> merge_asof, tolérance 5 jours.
    """
    dollar = get_series("DTWEXBGS", years=years)
    y10 = get_series("DGS10", years=years)

    dollar = dollar.rename(columns={"value": "dollar_index"}).sort_values("date")
    y10 = y10.rename(columns={"value": "yield_10y"}).sort_values("date")

    merged = pd.merge_asof(dollar, y10, on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=5))
    return merged.dropna(subset=["dollar_index", "yield_10y"]).reset_index(drop=True)


def generate():
    df = compute_dollar_vs_yield()

    if df.empty:
        raise RuntimeError(
            "[20_dollar_index_vs_10y_yield] Aucune donnée récupérée depuis FRED "
            "(DTWEXBGS/DGS10). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse bandes de récession et grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    line_dollar, = ax.plot(df["date"], df["dollar_index"], color=COLOR_ACCENT, linewidth=1.7,
                           label="Dollar pondéré échanges (éch. gauche)", zorder=3)
    line_yield, = ax2.plot(df["date"], df["yield_10y"], color=COLOR_YIELD, linewidth=1.2,
                           linestyle="--", label="Taux 10 ans US (%, éch. droite)", zorder=2)

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Indice dollar large (jan. 2006 = 100)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Taux 10 ans (%)", fontsize=9, color=COLOR_YIELD)
    ax2.tick_params(colors=COLOR_YIELD, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Dollar pondéré par les échanges vs taux 10 ans US",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    handles = [line_dollar, line_yield]
    ax.legend(handles, [h.get_label() for h in handles], loc="upper left",
              fontsize=8.5, frameon=False)

    pct = compute_percentile_rank(df["dollar_index"])
    ax.plot(last_row["date"], last_row["dollar_index"], marker="o", markersize=5,
            color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['dollar_index']:.1f}\nPercentile {HISTORY_YEARS} ans: {pct:.0f}e",
        xy=(last_row["date"], last_row["dollar_index"]),
        xytext=(10, 0), textcoords="offset points",
        fontsize=8.5, color=COLOR_ACCENT, fontweight="bold", va="center",
    )

    add_source_footer(
        fig,
        "Source: FRED (DTWEXBGS, DGS10) | Indice dollar large de la Fed, pondéré par les "
        "échanges commerciaux (base jan. 2006 = 100) -- pas le DXY",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "20_dollar_index_vs_10y_yield.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[20_dollar_index_vs_10y_yield] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
