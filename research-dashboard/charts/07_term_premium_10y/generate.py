"""
Graphique : Term Premium 10 ans (modèle Kim-Wright, Fed Board)

Séries FRED :
  - THREEFYTP10 : term premium à 10 ans, modèle Kim-Wright (Fed Board), quotidien
  - DGS10       : taux nominal du Trésor US à 10 ans, quotidien

Calcul : aucune transformation — on affiche directement le term premium et
le taux nominal, l'écart entre les deux représentant la composante
"anticipations de taux futurs" du rendement à 10 ans.

Pourquoi c'est utile : le rendement 10 ans se décompose en deux éléments :
(1) la moyenne des taux courts anticipés sur 10 ans, et (2) une prime de
risque (term premium) que les investisseurs exigent pour détenir une
obligation longue plutôt que de rouler des obligations courtes. Une hausse
du 10 ans tirée par la prime de risque (aversion au risque, incertitude
budgétaire) ne raconte pas la même histoire économique qu'une hausse tirée
par les anticipations de croissance/inflation. C'est un chart classique des
desks rates dans les notes de recherche GS/JPM.

Sortie : PNG dans output/{periode}/07_term_premium_10y.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, annotate_last_point_percentile, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

COLOR_NOMINAL = "#aaaaaa"


def compute_term_premium(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame avec colonnes: date, term_premium, nominal_10y."""
    term_premium = get_series("THREEFYTP10", years=years)
    nominal = get_series("DGS10", years=years)

    term_premium = term_premium.rename(columns={"value": "term_premium"}).sort_values("date")
    nominal = nominal.rename(columns={"value": "nominal_10y"}).sort_values("date")

    merged = pd.merge_asof(term_premium, nominal, on="date", direction="nearest", tolerance=pd.Timedelta(days=5))
    merged = merged.dropna(subset=["term_premium", "nominal_10y"])
    return merged.reset_index(drop=True)


def generate():
    df = compute_term_premium()

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["nominal_10y"], color=COLOR_NOMINAL, linewidth=1.3, linestyle="--",
            label="Taux nominal 10 ans (DGS10)")
    ax.plot(df["date"], df["term_premium"], color=COLOR_ACCENT, linewidth=2.0,
            label="Term Premium 10 ans (Kim-Wright, Fed Board)")
    ax.axhline(0, color="#999999", linewidth=0.8)

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("%", fontsize=9)
    ax.set_title("Term Premium 10 ans (modèle Kim-Wright, Fed Board)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    annotate_last_point_percentile(
        ax, last_row["date"], last_row["term_premium"], df["term_premium"],
        years_label=f"{HISTORY_YEARS} ans",
        value_label=f"{last_row['term_premium']:.2f}%",
    )

    add_source_footer(
        fig, "Source: FRED (THREEFYTP10, DGS10) | Modèle Kim-Wright, Federal Reserve Board",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "07_term_premium_10y.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[07_term_premium_10y] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
