"""
Graphique : Chicago Fed National Financial Conditions Index (NFCI)

Série FRED :
  - NFCI : indice composite hebdomadaire de la Fed de Chicago. Combine des
    dizaines de variables (taux, crédit, levier, volatilité) en un seul
    indice. Convention de lecture :
      - NFCI = 0   : conditions financières dans la moyenne historique
      - NFCI > 0   : conditions plus RESTRICTIVES que la moyenne
      - NFCI < 0   : conditions plus ACCOMMODANTES que la moyenne

Pourquoi c'est utile : un seul taux directeur ne dit pas grand-chose sur les
conditions financières réellement vécues par l'économie (accès au crédit,
levier, volatilité des marchés...). Le NFCI agrège tout ça en un indice
unique, plus riche pour juger si les conditions sont vraiment restrictives
dans l'économie réelle, au-delà du simple niveau des taux.

Sortie : PNG dans output/{periode}/06_nfci_financial_conditions.png
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


def compute_nfci(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame avec colonnes: date, nfci."""
    df = get_series("NFCI", years=years)
    return df.rename(columns={"value": "nfci"}).sort_values("date").reset_index(drop=True)


def generate():
    df = compute_nfci()

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["nfci"], color=COLOR_ACCENT, linewidth=1.8, label="NFCI")
    ax.axhline(0, color="#999999", linewidth=1.0)
    ax.text(df["date"].min(), 0.02, "Restrictif ↑", fontsize=7.5, color="#999999", va="bottom")
    ax.text(df["date"].min(), -0.02, "Accommodant ↓", fontsize=7.5, color="#999999", va="top")

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Indice (écart-type)", fontsize=9)
    ax.set_title("Chicago Fed National Financial Conditions Index (NFCI)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    annotate_last_point_percentile(
        ax, last_row["date"], last_row["nfci"], df["nfci"],
        years_label=f"{HISTORY_YEARS} ans",
        value_label=f"{last_row['nfci']:.2f}",
    )

    add_source_footer(
        fig, "Source: FRED (NFCI, Chicago Fed) | 0 = moyenne historique, >0 = restrictif, <0 = accommodant",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "06_nfci_financial_conditions.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[06_nfci_financial_conditions] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
