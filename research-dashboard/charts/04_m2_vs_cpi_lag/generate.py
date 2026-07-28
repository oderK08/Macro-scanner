"""
Graphique : M2 YoY vs CPI YoY (décalé de 15 mois)

Séries FRED :
  - M2SL      : masse monétaire M2, mensuel
  - CPIAUCSL  : indice des prix à la consommation (CPI), mensuel

Calcul : on calcule la variation annuelle (YoY %) des deux séries, puis on
décale la courbe CPI YoY de LAG_MONTHS mois vers la gauche sur le graphique
(en pratique : on affiche la valeur CPI YoY qui se produira LAG_MONTHS plus
tard, à la date d'aujourd'hui). Si la théorie du lag monétariste est
correcte, les deux courbes doivent visuellement se superposer.

Pourquoi c'est utile : ce décalage de 12-18 mois explique une bonne partie
de la trajectoire de l'inflation 2021-2023 avant même que les chiffres
officiels de CPI ne l'aient révélé — c'est un chart classique chez les
monétaristes (école Hanke et proches).

Sortie : PNG dans output/{periode}/04_m2_vs_cpi_lag.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, highlight_last_point, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

LAG_MONTHS = 15  # milieu de la fourchette 12-18 mois évoquée par la littérature monétariste
COLOR_CPI = "#c0392b"


def compute_m2_vs_cpi_lag(years: int = HISTORY_YEARS, lag_months: int = LAG_MONTHS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, m2_yoy, cpi_yoy_shifted.
    On télécharge davantage d'historique (years + 2 + lag) pour pouvoir
    calculer le YoY et appliquer le décalage sans trou de données sur la
    fenêtre affichée.
    """
    extra_years = 2 + (lag_months // 12) + 1
    m2 = get_series("M2SL", years=years + extra_years)
    cpi = get_series("CPIAUCSL", years=years + extra_years)

    m2 = m2.rename(columns={"value": "m2_index"}).sort_values("date").reset_index(drop=True)
    cpi = cpi.rename(columns={"value": "cpi_index"}).sort_values("date").reset_index(drop=True)

    m2["m2_yoy"] = m2["m2_index"].pct_change(periods=12) * 100
    cpi["cpi_yoy"] = cpi["cpi_index"].pct_change(periods=12) * 100

    # Décalage : on prend la valeur CPI YoY qui se produira `lag_months` plus
    # tard, et on l'associe à la date actuelle. Visuellement, la courbe CPI
    # se retrouve "translatée" vers la gauche par rapport à sa date réelle.
    cpi = cpi.sort_values("date").reset_index(drop=True)
    cpi["cpi_yoy_shifted"] = cpi["cpi_yoy"].shift(-lag_months)

    merged = pd.merge_asof(
        m2[["date", "m2_yoy"]].dropna(),
        cpi[["date", "cpi_yoy_shifted"]].dropna(),
        on="date",
        direction="nearest",
        tolerance=pd.Timedelta(days=20),
    )
    merged = merged.dropna(subset=["m2_yoy", "cpi_yoy_shifted"])

    date_min = merged["date"].max() - pd.DateOffset(years=years)
    return merged[merged["date"] >= date_min].reset_index(drop=True)


def generate():
    df = compute_m2_vs_cpi_lag()

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["m2_yoy"], color=COLOR_ACCENT, linewidth=2.0,
            label="M2 YoY (%)")
    ax.plot(df["date"], df["cpi_yoy_shifted"], color=COLOR_CPI, linewidth=1.8, linestyle="--",
            label=f"CPI YoY (%), décalé de {LAG_MONTHS} mois")
    ax.axhline(0, color="#999999", linewidth=0.8)

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("%", fontsize=9)
    ax.set_title(f"M2 YoY vs CPI YoY (décalé de {LAG_MONTHS} mois)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    highlight_last_point(
        ax, last_row["date"], last_row["m2_yoy"],
        value_label=f"M2 YoY: {last_row['m2_yoy']:.1f}%",
    )

    add_source_footer(
        fig,
        f"Source: FRED (M2SL, CPIAUCSL) | CPI décalé de {LAG_MONTHS} mois pour visualiser le lag monétaire",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "04_m2_vs_cpi_lag.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[04_m2_vs_cpi_lag] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
