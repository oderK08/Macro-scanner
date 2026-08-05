"""
Graphique : Dette nette / EBITDA par secteur (S&P 500, hors Financières)

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - Dette (composants À ADDITIONNER, comme chart 13) : DebtCurrent +
    LongTermDebtNoncurrent -- postes de BILAN ("instant", période CY..QI)
  - Trésorerie (fallback) : CashAndCashEquivalentsAtCarryingValue,
    CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents --
    poste de BILAN ("instant") aussi
  - EBITDA reconstruit (flux, "duration", période CY..Q sans I) :
    OperatingIncomeLoss + dotations aux amortissements (fallback :
    DepreciationDepletionAndAmortization et variantes)

Ce chart mélange donc concepts "instant" et "duration" pour un même
trimestre -- comme le chart 12 (inventaires/ventes). Le "I" final du format
de période EDGAR ne s'applique qu'aux postes de bilan.

Calcul, par secteur GICS et par trimestre :
    dette_nette = somme(dette) - somme(trésorerie)          [photo fin de trimestre]
    EBITDA_TTM  = TTM(somme(résultat op.)) + TTM(somme(D&A)) [flux lissé 4 trimestres]
    ratio       = dette_nette / EBITDA_TTM

Le secteur Financières est exclu : pour une banque, la dette est la matière
première du métier, pas un levier -- un ratio dette/EBITDA n'y a aucun sens
(même logique d'exclusion que l'ex-chart 14).

Pourquoi c'est utile : le debt-to-assets (chart 13) mesure le levier
BILANTIEL ; dette nette/EBITDA mesure la CAPACITÉ DE REMBOURSEMENT -- c'est
LA métrique des agences de notation et des covenants bancaires (seuils
usuels : <1x très sain, >3x levier élevé, >4x zone spéculative). Par
secteur, elle révèle où le levier s'accumule réellement, en tenant compte
de la trésorerie (des secteurs très endettés bruts peuvent être peu
endettés nets, et inversement).

Sortie : PNG dans output/{periode}/23_net_debt_ebitda_by_sector.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame
from common.sp500_list import get_sp500_constituents
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle
)
from common.config import (
    get_current_period_label, OUTPUT_DIR, DEBT_XBRL_CONCEPTS, CASH_XBRL_CONCEPTS,
    OPERATING_INCOME_XBRL_CONCEPTS, DEPRECIATION_AMORTIZATION_XBRL_CONCEPTS
)

DISPLAY_YEARS = 5
EXCLUDED_SECTORS = {"Financials"}  # la dette est leur matière première, ratio sans objet


def _sector_color_map(sectors: list) -> dict:
    """Même logique que le chart 11 : palette qualitative indexée par ordre
    alphabétique des secteurs réellement présents -- robuste si GICS évolue."""
    palette = plt.get_cmap("tab20").colors
    return {sector: palette[i % len(palette)] for i, sector in enumerate(sorted(sectors))}


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(concepts: list, period: str) -> dict:
    """Fusion de concepts alternatifs par CIK (le premier trouvé gagne),
    protégée contre les erreurs réseau -- même logique que charts 09/10/11."""
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


def _get_summed_frame_for_period(concepts: list, period: str) -> dict:
    """Somme de concepts COMPOSANTS par CIK (dette courante + long terme),
    pas des alternatives -- même logique que le chart 13."""
    total = {}
    for concept in concepts:
        try:
            frame_df = get_frame(concept, period)
        except Exception as e:
            print(f"  [avertissement] échec réseau pour {concept} / {period}: {e} -- ignoré, on continue")
            continue
        for _, row in frame_df.iterrows():
            cik = int(row["cik"])
            total[cik] = total.get(cik, 0) + row["value"]
    return total


def compute_net_debt_ebitda_by_sector(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame long: date, secteur, net_debt_ebitda."""
    constituents = get_sp500_constituents()
    constituents = constituents[~constituents["sector"].isin(EXCLUDED_SECTORS)]

    sector_ciks = {}
    for sector, group in constituents.groupby("sector"):
        sector_ciks[sector] = set(int(cik) for cik in group["cik"])

    current_year = datetime.today().year
    start_year = current_year - years - 1  # +1 an de marge pour le calcul TTM

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period_flow = f"CY{year}Q{quarter}"       # concepts "duration"
            period_instant = f"CY{year}Q{quarter}I"   # concepts de bilan

            debt_by_cik = _get_summed_frame_for_period(DEBT_XBRL_CONCEPTS, period_instant)
            cash_by_cik = _get_merged_frame_for_period(CASH_XBRL_CONCEPTS, period_instant)
            opinc_by_cik = _get_merged_frame_for_period(OPERATING_INCOME_XBRL_CONCEPTS, period_flow)
            dna_by_cik = _get_merged_frame_for_period(DEPRECIATION_AMORTIZATION_XBRL_CONCEPTS, period_flow)

            if not debt_by_cik or not opinc_by_cik:
                continue

            quarter_end = _quarter_end_date(year, quarter)
            for sector, ciks in sector_ciks.items():
                records.append({
                    "date": quarter_end,
                    "sector": sector,
                    "debt": sum(v for cik, v in debt_by_cik.items() if cik in ciks),
                    "cash": sum(v for cik, v in cash_by_cik.items() if cik in ciks),
                    "operating_income": sum(v for cik, v in opinc_by_cik.items() if cik in ciks),
                    "dna": sum(v for cik, v in dna_by_cik.items() if cik in ciks),
                })

    df_long = pd.DataFrame(records)
    if df_long.empty:
        return df_long

    results = []
    for sector in df_long["sector"].unique():
        sub = df_long[df_long["sector"] == sector].sort_values("date").set_index("date")
        ttm_ebitda = sub["operating_income"].rolling(window=4).sum() + sub["dna"].rolling(window=4).sum()
        net_debt = sub["debt"] - sub["cash"]
        ratio = net_debt / ttm_ebitda
        for date, val in ratio.items():
            # EBITDA TTM négatif ou nul : ratio sans signification, point exclu
            if pd.notna(val) and ttm_ebitda.loc[date] > 0:
                results.append({"date": date, "sector": sector, "net_debt_ebitda": val})

    ratio_df = pd.DataFrame(results)
    if ratio_df.empty:
        return ratio_df

    date_min_display = ratio_df["date"].max() - pd.DateOffset(years=years)
    return ratio_df[ratio_df["date"] >= date_min_display].reset_index(drop=True)


def generate():
    df = compute_net_debt_ebitda_by_sector()

    if df.empty:
        raise RuntimeError(
            "[23_net_debt_ebitda_by_sector] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau."
        )

    fig, ax = setup_figure()
    last_date = df["date"].max()

    sectors_present = sorted(df["sector"].unique())
    sector_colors = _sector_color_map(sectors_present)

    for sector in sectors_present:
        sub = df[df["sector"] == sector].sort_values("date")
        ax.plot(sub["date"], sub["net_debt_ebitda"], color=sector_colors[sector],
                linewidth=1.8, marker="o", markersize=3, label=sector)

    # Repères de lecture : seuils usuels agences de notation / covenants
    ax.axhline(3, color="#c0392b", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.axhline(0, color="#555555", linewidth=0.8, linestyle="--", alpha=0.6)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Dette nette / EBITDA TTM (x)", fontsize=9)
    ax.set_title("Dette nette / EBITDA par secteur GICS (S&P 500, hors Financières)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=7, frameon=False, ncol=2)

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Dette nette = dette totale - trésorerie, EBITDA = résultat op. + D&A (TTM) | "
        "Rouge: 3x, tirets: 0x (cash net)",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "23_net_debt_ebitda_by_sector.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[23_net_debt_ebitda_by_sector] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
