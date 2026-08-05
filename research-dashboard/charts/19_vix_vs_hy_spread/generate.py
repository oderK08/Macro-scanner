"""
Graphique : VIX vs spread crédit High Yield

Séries FRED :
  - VIXCLS       : indice VIX (volatilité implicite S&P 500 à 30 jours), quotidien
  - BAMLH0A0HYM2 : spread High Yield OAS (ICE BofA), quotidien, points de %

Pourquoi c'est utile : le VIX mesure le stress pricé par le marché ACTIONS
(via les options), le spread HY le stress pricé par le marché du CRÉDIT.
En régime normal, les deux évoluent ensemble. Les DIVERGENCES sont
l'information : un VIX écrasé avec des spreads qui s'élargissent
discrètement = le crédit voit un risque que les actions ignorent
(configuration pré-correction classique) ; des spreads serrés avec un VIX
élevé = stress de volatilité technique (positionnement, gamma) plutôt que
fondamental. Le chart 03 compare le crédit au NIVEAU des actions ; celui-ci
compare les deux prix du RISQUE entre eux.

Sortie : PNG dans output/{periode}/19_vix_vs_hy_spread.png
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

COLOR_VIX = "#7d3c98"


def compute_vix_vs_hy(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, vix, hy_spread.
    Deux séries quotidiennes (jours ouvrés) -> merge_asof, tolérance 5 jours.
    """
    vix = get_series("VIXCLS", years=years)
    hy = get_series("BAMLH0A0HYM2", years=years)

    vix = vix.rename(columns={"value": "vix"}).sort_values("date")
    hy = hy.rename(columns={"value": "hy_spread"}).sort_values("date")

    merged = pd.merge_asof(vix, hy, on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=5))
    return merged.dropna(subset=["vix", "hy_spread"]).reset_index(drop=True)


def generate():
    df = compute_vix_vs_hy()

    if df.empty:
        raise RuntimeError(
            "[19_vix_vs_hy_spread] Aucune donnée récupérée depuis FRED "
            "(VIXCLS/BAMLH0A0HYM2). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse bandes de récession et grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    line_vix, = ax.plot(df["date"], df["vix"], color=COLOR_VIX, linewidth=1.2,
                        label="VIX (éch. gauche)", zorder=2, alpha=0.85)
    line_hy, = ax2.plot(df["date"], df["hy_spread"], color=COLOR_ACCENT, linewidth=1.6,
                        label="Spread HY OAS (%, éch. droite)", zorder=3)

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("VIX", fontsize=9, color=COLOR_VIX)
    ax.tick_params(axis="y", colors=COLOR_VIX)
    ax2.set_ylabel("Spread HY OAS (%)", fontsize=9, color=COLOR_ACCENT)
    ax2.tick_params(colors=COLOR_ACCENT, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("VIX vs spread High Yield : les deux prix du risque",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    handles = [line_vix, line_hy]
    ax.legend(handles, [h.get_label() for h in handles], loc="upper left",
              fontsize=8.5, frameon=False)

    # Derniers points, avec le percentile de chacun : c'est la comparaison
    # des DEUX percentiles qui fait la lecture du chart (divergence ou pas)
    pct_vix = compute_percentile_rank(df["vix"])
    pct_hy = compute_percentile_rank(df["hy_spread"])
    ax.plot(last_row["date"], last_row["vix"], marker="o", markersize=5,
            color=COLOR_VIX, zorder=5)
    ax.annotate(
        f"VIX {last_row['vix']:.1f} (P{pct_vix:.0f})",
        xy=(last_row["date"], last_row["vix"]),
        xytext=(10, -5), textcoords="offset points",
        fontsize=8.5, color=COLOR_VIX, fontweight="bold", va="top",
    )
    ax2.plot(last_row["date"], last_row["hy_spread"], marker="o", markersize=5,
             color=COLOR_ACCENT, zorder=5)
    ax2.annotate(
        f"HY {last_row['hy_spread']:.2f}% (P{pct_hy:.0f})",
        xy=(last_row["date"], last_row["hy_spread"]),
        xytext=(10, 5), textcoords="offset points",
        fontsize=8.5, color=COLOR_ACCENT, fontweight="bold", va="bottom",
    )

    add_source_footer(
        fig,
        "Source: FRED (VIXCLS, BAMLH0A0HYM2) | P = percentile sur la fenêtre affichée. "
        "Divergence entre les deux percentiles = un marché price un risque que l'autre ignore",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "19_vix_vs_hy_spread.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[19_vix_vs_hy_spread] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
