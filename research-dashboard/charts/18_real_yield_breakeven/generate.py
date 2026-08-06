"""
Graphique : Taux réel 10 ans (TIPS) vs anticipations d'inflation (breakeven)

Séries FRED :
  - DFII10 : rendement réel du Trésor US 10 ans (TIPS), quotidien, %
  - T10YIE : breakeven d'inflation 10 ans (nominal - TIPS), quotidien, %

Ces deux séries décomposent le taux nominal 10 ans en ses deux composantes
observables sur le marché :

    taux nominal 10 ans ≈ taux réel (DFII10) + anticipations d'inflation (T10YIE)

Pourquoi c'est utile : quand le 10 ans nominal monte, la question qui
compte pour l'allocation est POURQUOI. Une hausse tirée par le taux réel
(coût du capital qui monte) comprime les valorisations actions -- surtout
les actifs de duration longue (tech, growth) -- et durcit réellement les
conditions financières. Une hausse tirée par le breakeven (anticipations
d'inflation) est un signal très différent : la politique monétaire perd en
crédibilité, les actifs réels/matières premières en profitent. Même
mouvement du nominal, implications opposées -- ce chart sépare les deux.

Sortie : PNG dans output/{periode}/18_real_yield_breakeven.png
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


def compute_real_yield_breakeven(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, real_yield, breakeven.
    Les deux séries sont quotidiennes (jours ouvrés) -> merge_asof avec
    petite tolérance par sécurité.
    """
    real_yield = get_series("DFII10", years=years)
    breakeven = get_series("T10YIE", years=years)

    real_yield = real_yield.rename(columns={"value": "real_yield"}).sort_values("date")
    breakeven = breakeven.rename(columns={"value": "breakeven"}).sort_values("date")

    merged = pd.merge_asof(real_yield, breakeven, on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=5))
    return merged.dropna(subset=["real_yield", "breakeven"]).reset_index(drop=True)


def generate():
    df = compute_real_yield_breakeven()

    if df.empty:
        raise RuntimeError(
            "[18_real_yield_breakeven] Aucune donnée récupérée depuis FRED "
            "(DFII10/T10YIE). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]
    ax.plot(df["date"], df["real_yield"], color=COLOR_ACCENT, linewidth=1.6,
            label=format_last_value_label("Taux réel 10 ans (TIPS)", f"{last_row['real_yield']:.2f}%",
                                          series=df["real_yield"], years_label=f"{HISTORY_YEARS} ans"),
            zorder=3)
    ax.plot(df["date"], df["breakeven"], color=COLOR_SECOND, linewidth=1.6,
            label=format_last_value_label("Breakeven d'inflation 10 ans",
                                          f"{last_row['breakeven']:.2f}%"),
            zorder=2)

    # Zéro : sous cette ligne, le taux réel est négatif (répression financière)
    ax.axhline(0, color="#555555", linewidth=0.9, linestyle="--", zorder=1)
    # Repère 2% : l'objectif d'inflation de la Fed, référence naturelle du breakeven
    ax.axhline(2, color=COLOR_SECOND, linewidth=0.7, linestyle=":", alpha=0.6, zorder=1)
    mark_last_point(ax, last_row["date"], last_row["real_yield"])
    mark_last_point(ax, last_row["date"], last_row["breakeven"], color=COLOR_SECOND)

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("%", fontsize=9)
    ax.set_title("Taux réel 10 ans vs anticipations d'inflation (breakeven 10 ans)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (DFII10, T10YIE) | Taux nominal 10 ans ≈ taux réel + breakeven. "
        "Pointillé rouge: objectif d'inflation Fed (2%)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "18_real_yield_breakeven.png")

    finalize_chart(fig, ax, out_path)

    print(f"[18_real_yield_breakeven] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
