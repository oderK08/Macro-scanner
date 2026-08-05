"""
Graphique : Croissance des profits vs croissance des cours (S&P 500)

Sources :
  - SEC EDGAR (frames) : résultat net agrégé des constituants du S&P 500
    (concept NetIncomeLoss -- le plus universellement tagué de tout US-GAAP),
    lissé TTM
  - FRED (SP500)       : niveau de l'indice S&P 500

Méthode : les deux séries sont rebasées à 100 au premier trimestre commun de
la fenêtre, puis superposées. L'écart entre les deux courbes est le proxy
d'expansion (ou de compression) de multiple.

Pourquoi c'est utile : c'est la version implémentable avec des données 100%
gratuites de la question de valorisation qu'un comité pose toujours -- "la
hausse du marché est-elle payée par les profits ou par l'expansion des
multiples ?". Un vrai P/E ou une vraie prime de risque exigerait les
capitalisations boursières par entreprise (données payantes) ; comparer les
CROISSANCES cumulées profits vs cours donne la même information de régime :
courbes parallèles = hausse saine payée par les profits ; cours qui
s'échappent au-dessus des profits = expansion de multiple (le marché paye
de plus en plus cher chaque dollar de profit) ; profits au-dessus des cours
= compression, le marché devient moins cher en relatif.

Sortie : PNG dans output/{periode}/24_earnings_growth_vs_price_growth.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame
from common.fred_client import get_series
from common.sp500_list import get_sp500_constituents
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle,
    COLOR_ACCENT
)
from common.config import (
    get_current_period_label, OUTPUT_DIR, NET_INCOME_XBRL_CONCEPTS
)

DISPLAY_YEARS = 5
COLOR_EARNINGS = "#2e7d52"


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(concepts: list, period: str) -> dict:
    """Fusion de concepts alternatifs par CIK, protégée contre les erreurs
    réseau -- même logique que charts 09/10/11."""
    combined = {}
    for concept in concepts:
        try:
            frame_df = get_frame(concept, period)
        except Exception as e:
            print(f"  [avertissement] échec réseau pour {concept} / {period}: {e} -- ignoré, on continue")
            continue
        if frame_df.empty:
            continue
        for _, row in frame_df.iterrows():
            cik = int(row["cik"])
            if cik not in combined:
                combined[cik] = row["value"]
    return combined


def compute_earnings_vs_price(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame: date, earnings_idx, price_idx (les deux rebasés
    à 100 au premier trimestre commun).
    """
    constituents = get_sp500_constituents()
    sp500_ciks = set(int(cik) for cik in constituents["cik"])

    current_year = datetime.today().year
    start_year = current_year - years - 1  # +1 an de marge pour le calcul TTM

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"
            ni_by_cik = _get_merged_frame_for_period(NET_INCOME_XBRL_CONCEPTS, period)
            if not ni_by_cik:
                continue
            records.append({
                "date": _quarter_end_date(year, quarter),
                "net_income": sum(v for cik, v in ni_by_cik.items() if cik in sp500_ciks),
            })

    earnings = pd.DataFrame(records)
    if earnings.empty:
        return earnings

    earnings = earnings.sort_values("date").set_index("date")
    earnings["earnings_ttm"] = earnings["net_income"].rolling(window=4).sum()
    earnings = earnings.dropna(subset=["earnings_ttm"]).reset_index()

    # Prix : niveau S&P 500 échantillonné à chaque fin de trimestre des
    # profits (merge_asof backward -- dernière clôture connue à cette date,
    # jamais une valeur future).
    sp500 = get_series("SP500", years=years + 2)
    sp500 = sp500.rename(columns={"value": "sp500"}).sort_values("date")
    merged = pd.merge_asof(earnings[["date", "earnings_ttm"]], sp500, on="date",
                           direction="backward", tolerance=pd.Timedelta(days=10))
    merged = merged.dropna(subset=["earnings_ttm", "sp500"])
    if merged.empty:
        return merged

    date_min_display = merged["date"].max() - pd.DateOffset(years=years)
    merged = merged[merged["date"] >= date_min_display].reset_index(drop=True)
    if merged.empty:
        return merged

    # Rebasage à 100 au premier trimestre commun de la fenêtre affichée
    merged["earnings_idx"] = merged["earnings_ttm"] / merged["earnings_ttm"].iloc[0] * 100
    merged["price_idx"] = merged["sp500"] / merged["sp500"].iloc[0] * 100
    return merged[["date", "earnings_idx", "price_idx"]]


def generate():
    df = compute_earnings_vs_price()

    if df.empty:
        raise RuntimeError(
            "[24_earnings_growth_vs_price_growth] Aucune donnée récupérée "
            "(EDGAR frames et/ou FRED SP500). Vérifie EDGAR_USER_AGENT, "
            "FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    last_row = df.iloc[-1]

    ax.plot(df["date"], df["price_idx"], color=COLOR_ACCENT, linewidth=2.0,
            marker="o", markersize=3, label="S&P 500 (cours)")
    ax.plot(df["date"], df["earnings_idx"], color=COLOR_EARNINGS, linewidth=2.0,
            marker="o", markersize=3, label="Résultat net agrégé TTM")

    ax.axhline(100, color="#555555", linewidth=0.8, linestyle="--", alpha=0.6)

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Indice (base 100 = début de fenêtre)", fontsize=9)
    ax.set_title("S&P 500 : croissance des cours vs croissance des profits",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    ax.plot(last_row["date"], last_row["price_idx"], marker="o", markersize=5,
            color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['price_idx']:.0f}",
        xy=(last_row["date"], last_row["price_idx"]),
        xytext=(10, 0), textcoords="offset points",
        fontsize=8.5, color=COLOR_ACCENT, fontweight="bold", va="center",
    )
    ax.plot(last_row["date"], last_row["earnings_idx"], marker="o", markersize=5,
            color=COLOR_EARNINGS, zorder=5)
    ax.annotate(
        f"{last_row['earnings_idx']:.0f}",
        xy=(last_row["date"], last_row["earnings_idx"]),
        xytext=(10, 0), textcoords="offset points",
        fontsize=8.5, color=COLOR_EARNINGS, fontweight="bold", va="center",
    )

    # L'écart final entre les deux indices est LE chiffre du chart : il
    # quantifie l'expansion/compression de multiple sur la fenêtre.
    gap = last_row["price_idx"] - last_row["earnings_idx"]
    regime = "expansion de multiple" if gap > 0 else "compression de multiple"
    ax.text(
        0.99, 0.03, f"Écart cours - profits : {gap:+.0f} pts ({regime})",
        transform=ax.transAxes, fontsize=8.5, color="#555555", ha="right", style="italic",
    )

    add_source_footer(
        fig,
        "Source: SEC EDGAR (NetIncomeLoss, frames API) + FRED (SP500) | "
        "Deux indices rebasés à 100 au début de la fenêtre. Écart = proxy d'expansion/compression de multiple",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "24_earnings_growth_vs_price_growth.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[24_earnings_growth_vs_price_growth] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
