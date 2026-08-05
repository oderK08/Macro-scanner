"""
Graphique : Liquidité nette de la Fed vs S&P 500

Séries FRED :
  - WALCL     : total du bilan de la Fed, hebdomadaire, en MILLIONS de $
  - RRPONTSYD : encours du Reverse Repo overnight (ON RRP), quotidien, en MILLIARDS de $
  - WTREGEN   : Treasury General Account (compte du Trésor à la Fed),
                hebdomadaire, en MILLIARDS de $

Calcul :
    liquidité_nette ($ trillions) = WALCL/1e6 - RRPONTSYD/1e3 - WTREGEN/1e3

ATTENTION aux unités : les trois séries FRED ne sont PAS dans la même unité
(WALCL en millions, les deux autres en milliards). Tout est converti en
trillions avant soustraction -- c'est l'erreur classique sur ce calcul.

Pourquoi c'est utile : le bilan brut de la Fed ne dit pas combien de
liquidité atteint réellement les marchés. Ce qui est parqué au Reverse Repo
ou sur le compte du Trésor (TGA) est stérilisé -- retiré du système. La
liquidité nette (bilan - RRP - TGA) est la mesure suivie par les desks
actions : sa corrélation avec le S&P 500 depuis 2020 en a fait un des
indicateurs de liquidité les plus regardés du marché. Le S&P 500 est
superposé (échelle droite) pour rendre les divergences visibles.

Sortie : PNG dans output/{periode}/16_net_liquidity_fed.png
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


def compute_net_liquidity(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, net_liquidity_tn, sp500.

    Base d'alignement : WALCL (hebdomadaire, publié le mercredi). Les autres
    séries sont raccrochées par merge_asof avec une tolérance de 7 jours --
    RRPONTSYD est quotidien, WTREGEN hebdomadaire, mais les jours exacts de
    publication peuvent différer (jours fériés).

    La colonne sp500 peut contenir des NaN en début de fenêtre (la série
    FRED SP500 ne couvre que ~10 ans glissants) : la liquidité nette reste
    tracée sur toute sa fenêtre, le S&P 500 uniquement là où il existe.
    """
    walcl = get_series("WALCL", years=years)          # millions $
    rrp = get_series("RRPONTSYD", years=years)        # milliards $
    tga = get_series("WTREGEN", years=years)          # milliards $
    sp500 = get_series("SP500", years=years)

    walcl = walcl.rename(columns={"value": "walcl"}).sort_values("date")
    rrp = rrp.rename(columns={"value": "rrp"}).sort_values("date")
    tga = tga.rename(columns={"value": "tga"}).sort_values("date")
    sp500 = sp500.rename(columns={"value": "sp500"}).sort_values("date")

    merged = pd.merge_asof(walcl, rrp, on="date", direction="nearest", tolerance=pd.Timedelta(days=7))
    merged = pd.merge_asof(merged, tga, on="date", direction="nearest", tolerance=pd.Timedelta(days=7))
    merged = pd.merge_asof(merged, sp500, on="date", direction="nearest", tolerance=pd.Timedelta(days=7))

    merged = merged.dropna(subset=["walcl", "rrp", "tga"])

    # Conversion en trillions AVANT soustraction (unités FRED hétérogènes,
    # voir docstring du module).
    merged["net_liquidity_tn"] = (
        merged["walcl"] / 1e6 - merged["rrp"] / 1e3 - merged["tga"] / 1e3
    )
    return merged[["date", "net_liquidity_tn", "sp500"]].reset_index(drop=True)


def generate():
    df = compute_net_liquidity()

    if df.empty:
        raise RuntimeError(
            "[16_net_liquidity_fed] Aucune donnée récupérée depuis FRED "
            "(WALCL/RRPONTSYD/WTREGEN). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse bandes de récession et grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]
    line_liq, = ax.plot(df["date"], df["net_liquidity_tn"], color=COLOR_ACCENT, linewidth=1.8,
                        label=format_last_value_label(
                            "Liquidité nette Fed ($T, éch. gauche)", f"{last_row['net_liquidity_tn']:.2f} T$",
                            series=df["net_liquidity_tn"], years_label=f"{HISTORY_YEARS} ans"),
                        zorder=3)

    sp500_available = df.dropna(subset=["sp500"])
    line_sp500 = None
    if not sp500_available.empty:
        line_sp500, = ax2.plot(sp500_available["date"], sp500_available["sp500"],
                               color=COLOR_BENCHMARK, linewidth=1.3, linestyle="--",
                               label=format_last_value_label(
                                   "S&P 500 (éch. droite)",
                                   f"{sp500_available['sp500'].iloc[-1]:.0f}"),
                               zorder=2)
    mark_last_point(ax, last_row["date"], last_row["net_liquidity_tn"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Liquidité nette ($ trillions)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("S&P 500", fontsize=9, color="#888888")
    ax2.tick_params(colors="#888888", labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Liquidité nette de la Fed (bilan - RRP - TGA) vs S&P 500",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (WALCL, RRPONTSYD, WTREGEN, SP500) | "
        "Liquidité nette = bilan Fed - Reverse Repo ON - Treasury General Account",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "16_net_liquidity_fed.png")

    finalize_chart(fig, ax, out_path,
                   handles=[h for h in [line_liq, line_sp500] if h is not None])

    print(f"[16_net_liquidity_fed] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
