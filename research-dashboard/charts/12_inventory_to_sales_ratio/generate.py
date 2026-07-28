"""
Graphique : Ratio inventaires/ventes par secteur

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - Inventaires : InventoryNet -- poste de BILAN (photo à une date donnée),
    donc concept "instant". Le format de période EDGAR est différent d'un
    concept de flux comme les revenus : "CY{year}Q{quarter}I" (avec un "I"
    final), et non "CY{year}Q{quarter}" comme pour Revenues/OperatingIncomeLoss.
    Oublier ce "I" est l'erreur la plus commune en travaillant avec l'API
    frames -- elle renvoie simplement une frame vide, pas une erreur explicite.
  - Revenus (fallback) : Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet

Calcul : ratio = inventaires (photo fin de trimestre) / chiffre d'affaires
TTM (glissant 12 mois) * 100 -- exprimé comme "% du chiffre d'affaires
annuel immobilisé en stock".

Pourquoi c'est utile : le ratio inventaires/ventes monte typiquement en fin
de cycle économique (les entreprises accumulent du stock qu'elles
n'arrivent plus à écouler aussi vite), et descend avant un restockage --
précurseur classique des cycles industriels et retail.

Sortie : PNG dans output/{periode}/12_inventory_to_sales_ratio.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle
)
from common.config import (
    get_current_period_label, OUTPUT_DIR, REVENUE_XBRL_CONCEPTS,
    INVENTORY_XBRL_CONCEPTS, SECTOR_TICKERS
)

SECTOR_COLORS = {
    "Technologie": "#1a3a5c",
    "Finance": "#c0392b",
    "Santé": "#2f6690",
    "Industrie": "#e08e79",
    "Énergie": "#5b8ab8",
    "Consommation": "#8fb8d8",
    "Télécoms": "#9b59b6",
    "Utilities": "#7f8c8d",
}

# Secteurs pertinents pour un ratio inventaires/ventes -- la Finance et les
# Télécoms/Utilities n'ont pas vraiment de "stock" au sens classique, on les
# exclut pour ne pas polluer le graphique avec des ratios non significatifs.
INVENTORY_RELEVANT_SECTORS = ["Technologie", "Industrie", "Énergie", "Consommation", "Santé"]

DISPLAY_YEARS = 5


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    """Retourne la date de fin du trimestre donné (dernier jour du mois)."""
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(concepts: list, period: str) -> dict:
    """
    Interroge tous les concepts XBRL candidats pour une période donnée,
    fusionne par CIK, protège chaque appel contre les erreurs réseau
    transitoires (même logique que charts 09/10/11).
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


def compute_inventory_to_sales(years: int = DISPLAY_YEARS, sectors: dict = None) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, secteur, inventory_to_sales_pct.
    Récupère years+1 an de données brutes en plus (marge pour le calcul du
    chiffre d'affaires en TTM).
    """
    if sectors is None:
        sectors = {k: v for k, v in SECTOR_TICKERS.items() if k in INVENTORY_RELEVANT_SECTORS}

    ticker_to_cik = get_ticker_to_cik_map()
    sector_ciks = {}
    for sector, tickers in sectors.items():
        ciks = set()
        for t in tickers:
            cik = ticker_to_cik.get(t.upper())
            if cik is not None:
                ciks.add(int(cik))
        sector_ciks[sector] = ciks

    current_year = datetime.today().year
    start_year = current_year - years - 1

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            duration_period = f"CY{year}Q{quarter}"
            instant_period = f"CY{year}Q{quarter}I"  # "I" = instant, obligatoire pour un poste de bilan

            revenue_by_cik = _get_merged_frame_for_period(REVENUE_XBRL_CONCEPTS, duration_period)
            inventory_by_cik = _get_merged_frame_for_period(INVENTORY_XBRL_CONCEPTS, instant_period)

            if not revenue_by_cik or not inventory_by_cik:
                continue

            quarter_end = _quarter_end_date(year, quarter)
            for sector, ciks in sector_ciks.items():
                sector_revenue = sum(v for cik, v in revenue_by_cik.items() if cik in ciks)
                sector_inventory = sum(v for cik, v in inventory_by_cik.items() if cik in ciks)
                if sector_revenue == 0:
                    continue
                records.append({
                    "date": quarter_end,
                    "sector": sector,
                    "revenue": sector_revenue,
                    "inventory": sector_inventory,
                })

    df_long = pd.DataFrame(records)
    if df_long.empty:
        return df_long

    results = []
    for sector in df_long["sector"].unique():
        sub = df_long[df_long["sector"] == sector].sort_values("date").set_index("date")
        ttm_revenue = sub["revenue"].rolling(window=4).sum()
        ratio = (sub["inventory"] / ttm_revenue) * 100
        for date, val in ratio.items():
            if pd.notna(val):
                results.append({"date": date, "sector": sector, "inventory_to_sales_pct": val})

    ratio_df = pd.DataFrame(results)
    if ratio_df.empty:
        return ratio_df

    date_min_display = ratio_df["date"].max() - pd.DateOffset(years=years)
    return ratio_df[ratio_df["date"] >= date_min_display].reset_index(drop=True)


def generate():
    df = compute_inventory_to_sales()

    if df.empty:
        raise RuntimeError(
            "[12_inventory_to_sales_ratio] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_date = df["date"].max()
    for sector in sorted(df["sector"].unique()):
        sub = df[df["sector"] == sector].sort_values("date")
        color = SECTOR_COLORS.get(sector, "#888888")
        ax.plot(sub["date"], sub["inventory_to_sales_pct"], color=color, linewidth=1.8,
                marker="o", markersize=3, label=sector)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Inventaires / CA annuel (%)", fontsize=9)
    ax.set_title("Ratio inventaires/ventes par secteur",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=2)

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Ratio = inventaires fin de trimestre / chiffre d'affaires TTM, "
        "échantillon de grandes capitalisations par secteur",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "12_inventory_to_sales_ratio.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[12_inventory_to_sales_ratio] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
