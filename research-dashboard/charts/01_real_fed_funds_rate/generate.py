"""
Graphique : Real Fed Funds Rate (taux directeur réel)

Calcul : FEDFUNDS - PCEPILFE_YoY
  - FEDFUNDS  : taux des fed funds effectif, nominal (FRED)
  - PCEPILFE  : Core PCE Price Index (déflateur préféré de la Fed),
                on calcule sa variation YoY (%) nous-mêmes.

Pourquoi c'est utile : la Fed communique en taux nominal, mais la politique
monétaire réellement restrictive/accommodante dépend du taux RÉEL. Si
l'inflation baisse plus vite que le taux nominal, le resserrement monétaire
s'intensifie tout seul, sans que la Fed ne bouge le taux nominal — ce chart
rend ce mécanisme visible.

Sortie : PNG dans output/{periode}/01_real_fed_funds_rate.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    annotate_last_point_percentile, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS


def compute_real_fed_funds_rate(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, nominal_rate, core_pce_yoy, real_rate.
    On télécharge un peu plus d'historique que nécessaire (years + 1) pour pouvoir
    calculer la variation YoY dès le premier point de la fenêtre affichée.
    """
    fedfunds = get_series("FEDFUNDS", years=years + 1)
    core_pce = get_series("PCEPILFE", years=years + 1)

    fedfunds = fedfunds.rename(columns={"value": "nominal_rate"})
    core_pce = core_pce.rename(columns={"value": "pce_index"})

    # PCEPILFE est mensuel -> on calcule la variation YoY (12 mois glissants)
    core_pce = core_pce.sort_values("date").reset_index(drop=True)
    core_pce["core_pce_yoy"] = core_pce["pce_index"].pct_change(periods=12) * 100

    merged = pd.merge_asof(
        fedfunds.sort_values("date"),
        core_pce[["date", "core_pce_yoy"]].sort_values("date"),
        on="date",
        direction="backward",
    )
    merged["real_rate"] = merged["nominal_rate"] - merged["core_pce_yoy"]
    merged = merged.dropna(subset=["real_rate"])

    # On restreint maintenant à la vraie fenêtre demandée
    date_min = merged["date"].max() - pd.DateOffset(years=years)
    return merged[merged["date"] >= date_min].reset_index(drop=True)


def generate():
    df = compute_real_fed_funds_rate()

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["nominal_rate"], color="#aaaaaa", linewidth=1.3,
            label="Taux nominal (Fed Funds)", linestyle="--")
    ax.plot(df["date"], df["real_rate"], color=COLOR_ACCENT, linewidth=2.0,
            label="Taux réel (Fed Funds - Core PCE YoY)")
    ax.axhline(0, color="#999999", linewidth=0.8)

    format_date_axis(ax)
    ax.set_ylabel("%", fontsize=9)
    ax.set_title("Taux directeur réel (Fed Funds - Core PCE YoY)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    last_row = df.iloc[-1]
    annotate_last_point_percentile(
        ax, last_row["date"], last_row["real_rate"], df["real_rate"], years_label=f"{HISTORY_YEARS} ans"
    )

    add_source_footer(fig, "Source: FRED (FEDFUNDS, PCEPILFE) | Calcul: taux nominal - Core PCE YoY")

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "01_real_fed_funds_rate.png")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[01_real_fed_funds_rate] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
