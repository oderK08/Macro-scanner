"""
Graphique : Debt Service Ratio vs Taux d'épargne des ménages

Séries FRED :
  - TDSP     : Household Debt Service Ratio, trimestriel, %
  - PSAVERT  : Personal Saving Rate, mensuel, %

Pourquoi c'est utile : ce chart aide à distinguer deux scénarios très
différents pour la consommation des ménages US. Si la consommation tient
alors que le debt service ratio est bas ET que le taux d'épargne est stable
ou en hausse, les ménages sont globalement sains. Si au contraire la
consommation tient uniquement parce que le taux d'épargne s'effondre
(les ménages puisent dans leurs réserves) ou que le debt service ratio
grimpe (les ménages s'endettent davantage pour maintenir leur niveau de
vie), la situation est plus fragile et moins soutenable dans la durée.

Sortie : PNG dans output/{periode}/08_debt_service_vs_savings.png
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

COLOR_SAVINGS = "#c0392b"


def compute_debt_service_vs_savings(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, debt_service_ratio, savings_rate.
    TDSP est trimestriel, PSAVERT est mensuel -> merge_asof avec tolérance
    large (100 jours) pour aligner correctement les deux fréquences.
    """
    debt_service = get_series("TDSP", years=years)
    savings = get_series("PSAVERT", years=years)

    debt_service = debt_service.rename(columns={"value": "debt_service_ratio"}).sort_values("date")
    savings = savings.rename(columns={"value": "savings_rate"}).sort_values("date")

    merged = pd.merge_asof(
        debt_service, savings, on="date", direction="nearest", tolerance=pd.Timedelta(days=100)
    )
    merged = merged.dropna(subset=["debt_service_ratio", "savings_rate"])
    return merged.reset_index(drop=True)


def generate():
    df = compute_debt_service_vs_savings()

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    line_debt, = ax.plot(df["date"], df["debt_service_ratio"], color=COLOR_ACCENT, linewidth=1.8,
                          label="Debt Service Ratio (%, éch. gauche)")
    line_savings, = ax2.plot(df["date"], df["savings_rate"], color=COLOR_SAVINGS, linewidth=1.5, linestyle="--",
                              label="Taux d'épargne (%, éch. droite)")

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Debt Service Ratio (%)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Taux d'épargne (%)", fontsize=9, color=COLOR_SAVINGS)
    ax2.tick_params(colors=COLOR_SAVINGS, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Debt Service Ratio vs Taux d'épargne des ménages",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    handles = [line_debt, line_savings]
    labels = [h.get_label() for h in handles]
    ax.legend(handles, labels, loc="upper left", fontsize=8.5, frameon=False)

    pct = compute_percentile_rank(df["debt_service_ratio"])
    ax.plot(last_row["date"], last_row["debt_service_ratio"], marker="o", markersize=5,
            color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['debt_service_ratio']:.2f}%\nPercentile {HISTORY_YEARS} ans: {pct:.0f}e",
        xy=(last_row["date"], last_row["debt_service_ratio"]),
        xytext=(55, 0),
        textcoords="offset points",
        fontsize=8.5,
        color=COLOR_ACCENT,
        fontweight="bold",
        va="center",
    )

    add_source_footer(
        fig, "Source: FRED (TDSP, PSAVERT)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "08_debt_service_vs_savings.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[08_debt_service_vs_savings] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
