"""
Graphique : Interest Coverage Ratio par groupe (Hyperscalers / Neoclouds /
Reste du S&P 500 hors Financières)

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - OperatingIncomeLoss : proxy d'EBIT (déjà utilisé au chart 11)
  - InterestExpense : charges d'intérêt, concept standard

Calcul : ratio = résultat opérationnel TTM / charges d'intérêt TTM. Les deux
concepts sont des flux ("duration"), lissés en TTM (glissant 4 trimestres)
pour la même raison que le chart 11 -- éviter le bruit trimestriel/saisonnier.

Le secteur Financier est exclu du groupe "Reste du S&P 500" : pour une
banque, les intérêts sont le cœur de métier (elle prête et emprunte en
permanence), donc un ratio de couverture d'intérêts n'a pas le même sens
que pour une entreprise non-financière -- l'inclure fausserait la
comparaison plutôt que de l'enrichir.

Pourquoi c'est utile : ce ratio mesure combien de fois le résultat
opérationnel couvre les charges d'intérêt -- plus il est élevé, plus
l'entreprise (ou le groupe) peut absorber une charge de dette sans mettre
en danger sa solvabilité. Comparer hyperscalers, neoclouds et reste du
marché révèle si le boom d'endettement IA a un vrai coussin de sécurité
ou navigue à vue.

Sortie : PNG dans output/{periode}/14_interest_coverage_ratio.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.sp500_list import get_sp500_constituents
from common.chart_style import setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle
from common.config import (
    get_current_period_label, OUTPUT_DIR, OPERATING_INCOME_XBRL_CONCEPTS,
    INTEREST_EXPENSE_XBRL_CONCEPTS, HYPERSCALER_TICKERS, NEOCLOUD_TICKERS
)

DISPLAY_YEARS = 5
GROUP_COLORS = {
    "Hyperscalers": "#1a3a5c",
    "Neoclouds": "#c0392b",
    "Reste du S&P 500 (hors Financières)": "#8fb8d8",
}


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(concepts: list, period: str) -> dict:
    """Fusionne plusieurs concepts XBRL alternatifs par CIK, protégé contre les erreurs réseau."""
    combined = {}
    for concept in concepts:
        try:
            frame_df = get_frame(concept, period)
        except Exception as e:
            print(f"  [avertissement] échec réseau pour {concept} / {period}: {e} -- ignoré")
            continue
        if frame_df.empty:
            continue
        for _, row in frame_df.iterrows():
            cik = int(row["cik"])
            if cik not in combined:
                combined[cik] = row["value"]
    return combined


def _build_group_ciks() -> dict:
    """
    Construit {nom_groupe: set(ciks)} pour Hyperscalers, Neoclouds, et le
    reste du S&P 500 hors secteur Financières.
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
    non_financial = constituents[constituents["sector"] != "Financials"]
    sp500_ciks = set(int(cik) for cik in non_financial["cik"])
    rest_ciks = sp500_ciks - hyperscaler_ciks

    return {
        "Hyperscalers": hyperscaler_ciks,
        "Neoclouds": neocloud_ciks,
        "Reste du S&P 500 (hors Financières)": rest_ciks,
    }


def compute_interest_coverage_by_group(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame long: date, groupe, interest_coverage_ratio."""
    group_ciks = _build_group_ciks()
    current_year = datetime.today().year
    start_year = current_year - years - 1  # +1 an de marge pour le calcul TTM

    raw_records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"

            opinc_by_cik = _get_merged_frame_for_period(OPERATING_INCOME_XBRL_CONCEPTS, period)
            interest_by_cik = _get_merged_frame_for_period(INTEREST_EXPENSE_XBRL_CONCEPTS, period)

            if not opinc_by_cik or not interest_by_cik:
                continue

            quarter_end = _quarter_end_date(year, quarter)
            for group_name, ciks in group_ciks.items():
                group_opinc = sum(v for cik, v in opinc_by_cik.items() if cik in ciks)
                group_interest = sum(v for cik, v in interest_by_cik.items() if cik in ciks)
                if group_interest == 0:
                    continue
                raw_records.append({
                    "date": quarter_end,
                    "group": group_name,
                    "operating_income": group_opinc,
                    "interest_expense": group_interest,
                })

    df_long = pd.DataFrame(raw_records)
    if df_long.empty:
        return df_long

    results = []
    for group in df_long["group"].unique():
        sub = df_long[df_long["group"] == group].sort_values("date").set_index("date")
        ttm_opinc = sub["operating_income"].rolling(window=4).sum()
        ttm_interest = sub["interest_expense"].rolling(window=4).sum()
        ratio = ttm_opinc / ttm_interest
        for date, val in ratio.items():
            if pd.notna(val):
                results.append({"date": date, "group": group, "interest_coverage_ratio": val})

    ratio_df = pd.DataFrame(results)
    if ratio_df.empty:
        return ratio_df

    date_min_display = ratio_df["date"].max() - pd.DateOffset(years=years)
    return ratio_df[ratio_df["date"] >= date_min_display].reset_index(drop=True)


def generate():
    df = compute_interest_coverage_by_group()

    if df.empty:
        raise RuntimeError(
            "[14_interest_coverage_ratio] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau."
        )

    fig, ax = setup_figure()
    last_date = df["date"].max()

    for group in ["Hyperscalers", "Neoclouds", "Reste du S&P 500 (hors Financières)"]:
        sub = df[df["group"] == group].sort_values("date")
        if sub.empty:
            continue
        ax.plot(sub["date"], sub["interest_coverage_ratio"], color=GROUP_COLORS[group],
                linewidth=2.0, marker="o", markersize=3, label=group)

    ax.axhline(1, color="#c0392b", linewidth=0.8, linestyle=":")
    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Résultat opérationnel TTM / Intérêts TTM (x)", fontsize=9)
    ax.set_title("Interest Coverage Ratio : Hyperscalers vs Neoclouds vs reste du marché",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=8, frameon=False)

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Ratio = OperatingIncomeLoss TTM / InterestExpense TTM. "
        "Hyperscalers: MSFT/GOOGL/AMZN/META. Neoclouds: CRWV/NBIS/IREN/APLD/CORZ/WULF/CIFR.",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "14_interest_coverage_ratio.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[14_interest_coverage_ratio] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
