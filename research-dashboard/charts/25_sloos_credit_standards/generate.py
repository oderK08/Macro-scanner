"""
Graphique : Conditions de crédit bancaire (SLOOS) vs spread High Yield

Séries FRED :
  - DRTSCILM     : Senior Loan Officer Opinion Survey -- % net de banques
                   domestiques durcissant leurs standards de prêt C&I
                   (Commercial & Industrial) aux grandes/moyennes entreprises,
                   trimestriel, points de %
  - BAMLH0A0HYM2 : spread High Yield OAS (ICE BofA), quotidien, points de %

Pourquoi c'est utile : le SLOOS est l'enquête trimestrielle de la Fed
auprès des directeurs de crédit des banques -- elle mesure le robinet du
crédit à la source, avant que le durcissement ne se voie dans les défauts
ou les spreads. Historiquement, un pic de durcissement PRÉCÈDE la montée
des défauts et la récession de 3 à 4 trimestres. La superposition avec le
spread HY répond à la question que pose un comité : le marché du crédit
price-t-il déjà ce que les banques font ? Un SLOOS qui se durcit avec des
spreads encore serrés est la divergence la plus dangereuse -- le coût du
risque monte à la source mais n'est pas encore payé par les investisseurs.

Sortie : PNG dans output/{periode}/25_sloos_credit_standards.png
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
    finalize_chart, COLOR_ACCENT, COLOR_SECOND
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS


def compute_sloos_vs_hy(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, sloos_tightening, hy_spread.
    DRTSCILM est trimestriel, le spread HY quotidien : le spread est
    raccroché à chaque date SLOOS par merge_asof backward (dernière valeur
    connue à la date de l'enquête, jamais une valeur future).
    """
    sloos = get_series("DRTSCILM", years=years)
    hy = get_series("BAMLH0A0HYM2", years=years)

    sloos = sloos.rename(columns={"value": "sloos_tightening"}).sort_values("date")
    hy = hy.rename(columns={"value": "hy_spread"}).sort_values("date")

    merged = pd.merge_asof(sloos, hy, on="date", direction="backward",
                           tolerance=pd.Timedelta(days=10))
    return merged.dropna(subset=["sloos_tightening"]).reset_index(drop=True)


def generate():
    df = compute_sloos_vs_hy()

    if df.empty:
        raise RuntimeError(
            "[25_sloos_credit_standards] Aucune donnée récupérée depuis FRED "
            "(DRTSCILM/BAMLH0A0HYM2). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse bandes de récession et grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]
    line_sloos, = ax.plot(df["date"], df["sloos_tightening"], color=COLOR_ACCENT,
                          linewidth=2.0, marker="o", markersize=3,
                          label=format_last_value_label(
                              "Banques durcissant leurs standards C&I (% net, éch. gauche)",
                              f"{last_row['sloos_tightening']:+.1f}%",
                              series=df["sloos_tightening"], years_label=f"{HISTORY_YEARS} ans"))

    hy_available = df.dropna(subset=["hy_spread"])
    line_hy = None
    if not hy_available.empty:
        line_hy, = ax2.plot(hy_available["date"], hy_available["hy_spread"], color=COLOR_SECOND,
                            linewidth=1.5, linestyle="--",
                            label=format_last_value_label(
                                "Spread HY OAS (%, éch. droite)",
                                f"{hy_available['hy_spread'].iloc[-1]:.2f}%"))

    # Zéro : au-dessus, plus de banques durcissent qu'elles n'assouplissent
    ax.axhline(0, color="#555555", linewidth=0.9, linestyle="--", zorder=1)
    mark_last_point(ax, last_row["date"], last_row["sloos_tightening"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("% net de banques durcissant", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Spread HY OAS (%)", fontsize=9, color=COLOR_SECOND)
    ax2.tick_params(colors=COLOR_SECOND, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Conditions de crédit bancaire (SLOOS) vs spread High Yield",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (DRTSCILM -- enquête SLOOS de la Fed, BAMLH0A0HYM2) | "
        "SLOOS > 0 = resserrement net du crédit bancaire. Le durcissement précède "
        "historiquement défauts et récession de 3-4 trimestres",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "25_sloos_credit_standards.png")

    handles = [h for h in [line_sloos, line_hy] if h is not None]
    finalize_chart(fig, ax, out_path, handles=handles)

    print(f"[25_sloos_credit_standards] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
