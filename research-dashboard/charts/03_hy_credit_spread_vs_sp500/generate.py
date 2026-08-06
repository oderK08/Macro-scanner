"""
Graphique : HY Credit Spread vs S&P 500

Séries FRED :
  - BAMLH0A0HYM2 : spread High Yield OAS (ICE BofA), quotidien, en points de %
  - SP500        : niveau de l'indice S&P 500, quotidien

Pourquoi c'est utile : le marché du crédit "sait" souvent avant les actions.
Le spread HY s'élargit fréquemment 1 à 2 mois avant une correction actions
significative — les investisseurs obligataires réagissent au risque de
défaut avant que le risque ne soit pricé en actions. Ce chart superpose les
deux pour repérer visuellement ces décalages.

Sortie : PNG dans output/{periode}/03_hy_credit_spread_vs_sp500.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, mark_last_point, format_last_value_label,
    finalize_chart, COLOR_ACCENT, COLOR_BENCHMARK
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS


def compute_hy_spread_vs_sp500(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, hy_spread, sp500.
    Les deux séries FRED sont quotidiennes mais pas toujours publiées les
    mêmes jours exacts (jours fériés différents) -> merge_asof pour aligner.
    """
    hy_spread = get_series("BAMLH0A0HYM2", years=years)
    sp500 = get_series("SP500", years=years)

    hy_spread = hy_spread.rename(columns={"value": "hy_spread"}).sort_values("date")
    sp500 = sp500.rename(columns={"value": "sp500"}).sort_values("date")

    merged = pd.merge_asof(hy_spread, sp500, on="date", direction="nearest", tolerance=pd.Timedelta(days=5))
    merged = merged.dropna(subset=["hy_spread", "sp500"])
    return merged.reset_index(drop=True)


def generate():
    df = compute_hy_spread_vs_sp500()

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse les bandes de récession et la grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]
    line_spread, = ax.plot(df["date"], df["hy_spread"], color=COLOR_ACCENT, linewidth=1.8,
                           label=format_last_value_label(
                               "Spread HY OAS (%, éch. gauche)", f"{last_row['hy_spread']:.2f}%",
                               series=df["hy_spread"], years_label=f"{HISTORY_YEARS} ans"),
                           zorder=3)
    line_sp500, = ax2.plot(df["date"], df["sp500"], color=COLOR_BENCHMARK, linewidth=1.3, linestyle="--",
                           label=format_last_value_label("S&P 500 (éch. droite)",
                                                         f"{last_row['sp500']:.0f}"),
                           zorder=2)
    mark_last_point(ax, last_row["date"], last_row["hy_spread"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Spread HY OAS (%)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("S&P 500", fontsize=9, color="#888888")
    ax2.tick_params(colors="#888888", labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Spread crédit High Yield vs S&P 500",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig, "Source: FRED (BAMLH0A0HYM2, SP500)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "03_hy_credit_spread_vs_sp500.png")

    # Légende combinée passée explicitement (les deux lignes vivent sur deux axes)
    finalize_chart(fig, ax, out_path, handles=[line_spread, line_sp500])

    print(f"[03_hy_credit_spread_vs_sp500] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
