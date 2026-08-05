"""
Graphique : Debt-to-Assets par groupe (Hyperscalers / Neoclouds / Reste du S&P 500)

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - Assets : total des actifs, concept standard, quasi toujours tagué
  - Dette totale : DebtCurrent + LongTermDebtNoncurrent -- ATTENTION, ces
    deux concepts sont des COMPOSANTS À ADDITIONNER (portion courante +
    portion long terme de la dette), pas des alternatives comme pour le
    capex/revenus où un seul concept "gagne".

Les deux concepts sont des postes de BILAN ("instant"), donc le format de
période EDGAR utilise le suffixe "I" pour les deux (contrairement au chart
12 qui mélangeait un concept instant et un concept duration).

Pourquoi c'est utile : le narratif "les hyperscalers financent leur boom
capex par la dette" mérite d'être confronté aux chiffres -- comparer leur
levier (dette/actifs) à celui des neoclouds (modèle plus capital-intensif,
souvent plus endetté) et au reste du marché permet de juger si le risque de
levier est concentré, généralisé, ou en réalité plus prudent qu'on ne le
pense pour les hyperscalers spécifiquement.

Sortie : PNG dans output/{periode}/13_debt_to_assets_by_group.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.sp500_list import get_sp500_constituents
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle,
    finalize_chart, COLOR_ACCENT, COLOR_SECOND, COLOR_THIRD
)
from common.config import (
    get_current_period_label, OUTPUT_DIR, DEBT_XBRL_CONCEPTS,
    HYPERSCALER_TICKERS, NEOCLOUD_TICKERS
)

DISPLAY_YEARS = 5
GROUP_COLORS = {
    "Hyperscalers": COLOR_ACCENT,
    "Neoclouds": COLOR_SECOND,
    "Reste du S&P 500": COLOR_THIRD,
}


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_frame_dict(concept: str, period: str) -> dict:
    """Récupère un concept pour une période, protégé contre les erreurs réseau. Retourne {cik: value}."""
    try:
        frame_df = get_frame(concept, period)
    except Exception as e:
        print(f"  [avertissement] échec réseau pour {concept} / {period}: {e} -- ignoré")
        return {}
    if frame_df.empty:
        return {}
    return {int(row["cik"]): row["value"] for _, row in frame_df.iterrows()}


def _get_summed_debt(period_instant: str) -> dict:
    """
    Somme DebtCurrent + LongTermDebtNoncurrent par CIK (composants additifs,
    pas des alternatives -- voir docstring du module).
    """
    total = {}
    for concept in DEBT_XBRL_CONCEPTS:
        frame = _get_frame_dict(concept, period_instant)
        for cik, value in frame.items():
            total[cik] = total.get(cik, 0) + value
    return total


def _build_group_ciks() -> dict:
    """
    Construit {nom_groupe: set(ciks)} pour Hyperscalers, Neoclouds, et le
    reste du S&P 500 (constituants S&P 500 moins les hyperscalers, qui en
    font déjà partie).
    """
    ticker_to_cik = get_ticker_to_cik_map()

    hyperscaler_ciks = set()
    for t in HYPERSCALER_TICKERS:
        cik = ticker_to_cik.get(t.upper())
        if cik:
            hyperscaler_ciks.add(int(cik))

    neocloud_ciks = set()
    for t in NEOCLOUD_TICKERS:
        cik = ticker_to_cik.get(t.upper())
        if cik:
            neocloud_ciks.add(int(cik))

    constituents = get_sp500_constituents()
    sp500_ciks = set(int(cik) for cik in constituents["cik"])
    rest_ciks = sp500_ciks - hyperscaler_ciks

    return {
        "Hyperscalers": hyperscaler_ciks,
        "Neoclouds": neocloud_ciks,
        "Reste du S&P 500": rest_ciks,
    }


def compute_debt_to_assets_by_group(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame long: date, groupe, debt_to_assets_pct."""
    group_ciks = _build_group_ciks()
    current_year = datetime.today().year
    start_year = current_year - years

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period_instant = f"CY{year}Q{quarter}I"

            assets_by_cik = _get_frame_dict("Assets", period_instant)
            if not assets_by_cik:
                continue
            debt_by_cik = _get_summed_debt(period_instant)
            if not debt_by_cik:
                continue

            quarter_end = _quarter_end_date(year, quarter)
            for group_name, ciks in group_ciks.items():
                group_assets = sum(v for cik, v in assets_by_cik.items() if cik in ciks)
                group_debt = sum(v for cik, v in debt_by_cik.items() if cik in ciks)
                if group_assets == 0:
                    continue
                records.append({
                    "date": quarter_end,
                    "group": group_name,
                    "debt_to_assets_pct": (group_debt / group_assets) * 100,
                })

    return pd.DataFrame(records)


def generate():
    df = compute_debt_to_assets_by_group()

    if df.empty:
        raise RuntimeError(
            "[13_debt_to_assets_by_group] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau."
        )

    fig, ax = setup_figure()
    last_date = df["date"].max()

    for group in ["Hyperscalers", "Neoclouds", "Reste du S&P 500"]:
        sub = df[df["group"] == group].sort_values("date")
        if sub.empty:
            continue
        ax.plot(sub["date"], sub["debt_to_assets_pct"], color=GROUP_COLORS[group],
                linewidth=2.0, marker="o", markersize=3, label=group)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Dette / Actifs totaux (%)", fontsize=9)
    ax.set_title("Debt-to-Assets : Hyperscalers vs Neoclouds vs reste du S&P 500",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Dette = DebtCurrent + LongTermDebtNoncurrent, "
        "Actifs = Assets. Hyperscalers: MSFT/GOOGL/AMZN/META. Neoclouds: CRWV/NBIS/IREN/APLD/CORZ/WULF/CIFR.",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "13_debt_to_assets_by_group.png")

    finalize_chart(fig, ax, out_path, legend_ncol=3)

    print(f"[13_debt_to_assets_by_group] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
