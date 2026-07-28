"""
Graphique : JOLTS Quits Rate vs croissance des salaires

Séries FRED :
  - JTSQUR          : taux de démission volontaire (Quits Rate), mensuel, %
  - CES0500000003   : salaire horaire moyen, secteur privé, mensuel ($/h)
                       -> on calcule sa variation annuelle (YoY %) nous-mêmes

Pourquoi c'est utile : les gens ne quittent leur emploi volontairement que
s'ils sont confiants de retrouver mieux ailleurs. Le taux de démission est
donc un indicateur avancé de la tension sur le marché du travail — il
précède généralement l'inflation salariale de plusieurs mois, contrairement
au taux de chômage qui est un indicateur plutôt coïncident/retardé.

Sortie : PNG dans output/{periode}/05_jolts_quits_vs_wages.png
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

COLOR_WAGES = "#c0392b"


def compute_quits_vs_wages(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, quits_rate, wage_yoy.
    Le salaire est téléchargé avec 1 an de marge en plus pour pouvoir
    calculer sa variation YoY dès le premier point affiché.
    """
    quits = get_series("JTSQUR", years=years)
    wages = get_series("CES0500000003", years=years + 1)

    quits = quits.rename(columns={"value": "quits_rate"}).sort_values("date")
    wages = wages.rename(columns={"value": "wage_level"}).sort_values("date").reset_index(drop=True)
    wages["wage_yoy"] = wages["wage_level"].pct_change(periods=12) * 100

    merged = pd.merge_asof(
        quits, wages[["date", "wage_yoy"]].dropna(),
        on="date", direction="nearest", tolerance=pd.Timedelta(days=20),
    )
    merged = merged.dropna(subset=["quits_rate", "wage_yoy"])

    date_min = merged["date"].max() - pd.DateOffset(years=years)
    return merged[merged["date"] >= date_min].reset_index(drop=True)


def generate():
    df = compute_quits_vs_wages()

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    line_quits, = ax.plot(df["date"], df["quits_rate"], color=COLOR_ACCENT, linewidth=1.8,
                           label="Quits Rate (%, éch. gauche)")
    line_wages, = ax2.plot(df["date"], df["wage_yoy"], color=COLOR_WAGES, linewidth=1.5, linestyle="--",
                            label="Salaire horaire YoY (%, éch. droite)")

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Quits Rate (%)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Salaire YoY (%)", fontsize=9, color=COLOR_WAGES)
    ax2.tick_params(colors=COLOR_WAGES, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("JOLTS Quits Rate vs croissance des salaires",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    handles = [line_quits, line_wages]
    labels = [h.get_label() for h in handles]
    ax.legend(handles, labels, loc="upper left", fontsize=8.5, frameon=False)

    pct = compute_percentile_rank(df["quits_rate"])
    ax.plot(last_row["date"], last_row["quits_rate"], marker="o", markersize=5, color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['quits_rate']:.2f}%\nPercentile {HISTORY_YEARS} ans: {pct:.0f}e",
        xy=(last_row["date"], last_row["quits_rate"]),
        xytext=(55, 0),
        textcoords="offset points",
        fontsize=8.5,
        color=COLOR_ACCENT,
        fontweight="bold",
        va="center",
    )

    add_source_footer(
        fig, "Source: FRED (JTSQUR, CES0500000003)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "05_jolts_quits_vs_wages.png")

    fig.tight_layout(rect=[0, 0.05, 0.82, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[05_jolts_quits_vs_wages] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
