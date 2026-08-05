"""
Graphique : Rachats d'actions vs Capex agrégés du S&P 500

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - Rachats (fallback) : PaymentsForRepurchaseOfCommonStock,
                          PaymentsForRepurchaseOfEquity
  - Capex (fallback)   : PaymentsToAcquirePropertyPlantAndEquipment,
                          PaymentsForCapitalImprovements,
                          PaymentsToAcquireProductiveAssets

Méthode : pour chaque trimestre, somme des rachats et du capex de tous les
constituants actuels du S&P 500 trouvés dans les frames EDGAR, puis lissage
TTM (glissant 4 trimestres) -- même mécanique que les charts 09/11.

Pourquoi c'est utile : rachats et capex sont les deux grands usages
concurrents du cash-flow des entreprises. Leur ratio est un baromètre de
régime : capex > rachats = les entreprises voient des opportunités
d'investissement rentables (ou y sont contraintes -- boom IA) ; rachats >
capex = retour aux actionnaires privilégié, soutien technique aux cours
mais parfois symptôme d'un manque d'idées de croissance. Le basculement de
régime en cours (boom capex IA financé en partie au détriment des rachats
chez certaines méga-caps) est exactement ce que ce chart rend visible.

Sortie : PNG dans output/{periode}/22_buybacks_vs_capex.png
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
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle,
    mark_last_point, format_last_value_label, finalize_chart,
    COLOR_ACCENT, COLOR_SECOND
)
from common.config import (
    get_current_period_label, OUTPUT_DIR, BUYBACK_XBRL_CONCEPTS, CAPEX_XBRL_CONCEPTS
)

# Fenêtre courte comme les autres charts EDGAR : le coût API du détail
# trimestriel sur 10 ans ne se justifie pas, 5 ans suffisent à voir le régime.
DISPLAY_YEARS = 5


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(concepts: list, period: str) -> dict:
    """
    Interroge tous les concepts XBRL candidats pour une période donnée,
    fusionne par CIK (le premier concept trouvé gagne), protégé contre les
    erreurs réseau transitoires -- même logique que les charts 09/10/11.
    """
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


def compute_buybacks_vs_capex(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame: date, buybacks_bn, capex_bn (TTM, milliards $).
    Récupère 1 an de données brutes en plus (marge pour le calcul TTM).
    """
    constituents = get_sp500_constituents()
    sp500_ciks = set(int(cik) for cik in constituents["cik"])

    current_year = datetime.today().year
    start_year = current_year - years - 1

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"

            buybacks_by_cik = _get_merged_frame_for_period(BUYBACK_XBRL_CONCEPTS, period)
            capex_by_cik = _get_merged_frame_for_period(CAPEX_XBRL_CONCEPTS, period)

            if not buybacks_by_cik or not capex_by_cik:
                continue

            records.append({
                "date": _quarter_end_date(year, quarter),
                "buybacks": sum(v for cik, v in buybacks_by_cik.items() if cik in sp500_ciks),
                "capex": sum(v for cik, v in capex_by_cik.items() if cik in sp500_ciks),
            })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = df.sort_values("date").set_index("date")
    ttm = pd.DataFrame({
        "buybacks_bn": df["buybacks"].rolling(window=4).sum() / 1e9,
        "capex_bn": df["capex"].rolling(window=4).sum() / 1e9,
    }).dropna().reset_index()

    if ttm.empty:
        return ttm

    date_min_display = ttm["date"].max() - pd.DateOffset(years=years)
    return ttm[ttm["date"] >= date_min_display].reset_index(drop=True)


def generate():
    df = compute_buybacks_vs_capex()

    if df.empty:
        raise RuntimeError(
            "[22_buybacks_vs_capex] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau."
        )

    fig, ax = setup_figure()
    last_row = df.iloc[-1]

    ax.plot(df["date"], df["capex_bn"], color=COLOR_ACCENT, linewidth=2.0,
            marker="o", markersize=3,
            label=format_last_value_label("Capex TTM", f"{last_row['capex_bn']:.0f} Md$"))
    ax.plot(df["date"], df["buybacks_bn"], color=COLOR_SECOND, linewidth=2.0,
            marker="o", markersize=3,
            label=format_last_value_label("Rachats d'actions TTM",
                                          f"{last_row['buybacks_bn']:.0f} Md$"))
    mark_last_point(ax, last_row["date"], last_row["capex_bn"])
    mark_last_point(ax, last_row["date"], last_row["buybacks_bn"], color=COLOR_SECOND)

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Milliards de $ (TTM)", fontsize=9)
    ax.set_title("S&P 500 : rachats d'actions vs capex (agrégés, TTM)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Constituants actuels du S&P 500 (Wikipedia). "
        "Rachats = PaymentsForRepurchaseOfCommonStock (et variantes), Capex = PP&E acquis (et variantes)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "22_buybacks_vs_capex.png")

    finalize_chart(fig, ax, out_path)

    print(f"[22_buybacks_vs_capex] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
