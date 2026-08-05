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

from common.edgar_client import get_frame
from common.sp500_list import get_sp500_constituents
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, finalize_chart
)
from common.config import get_current_period_label, OUTPUT_DIR, REVENUE_XBRL_CONCEPTS, INVENTORY_XBRL_CONCEPTS

# Secteurs GICS pertinents pour un ratio inventaires/ventes -- la Finance,
# les Télécoms/Utilities/Immobilier n'ont pas vraiment de "stock" au sens
# classique (services, infrastructure), on les exclut pour ne pas polluer
# le graphique avec des ratios non significatifs.
INVENTORY_RELEVANT_SECTORS = [
    "Information Technology", "Industrials", "Energy", "Consumer Discretionary",
    "Consumer Staples", "Health Care", "Materials",
]

DISPLAY_YEARS = 5


def _sector_color_map(sectors: list) -> dict:
    """
    Génère une couleur distincte par secteur à partir d'une palette
    qualitative standard (tab20), indexée par ordre alphabétique -- robuste
    si GICS ajoute/renomme un secteur un jour (voir chart 11 pour la même
    logique).
    """
    palette = plt.get_cmap("tab20").colors
    return {sector: palette[i % len(palette)] for i, sector in enumerate(sorted(sectors))}


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


def compute_inventory_to_sales(years: int = DISPLAY_YEARS, constituents: pd.DataFrame = None) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, secteur, inventory_to_sales_pct.
    Récupère years+1 an de données brutes en plus (marge pour le calcul du
    chiffre d'affaires en TTM).

    `constituents` : DataFrame optionnel (colonnes ticker, sector, cik) --
    si non fourni, va chercher la vraie composition actuelle du S&P 500 via
    common.sp500_list, restreinte aux secteurs pertinents pour un ratio
    inventaires/ventes (INVENTORY_RELEVANT_SECTORS).
    """
    if constituents is None:
        constituents = get_sp500_constituents()

    relevant = constituents[constituents["sector"].isin(INVENTORY_RELEVANT_SECTORS)]
    sector_ciks = {}
    for sector, group in relevant.groupby("sector"):
        sector_ciks[sector] = set(int(cik) for cik in group["cik"])

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
                sector_inventory_ciks = [cik for cik in ciks if cik in inventory_by_cik]
                sector_inventory = sum(inventory_by_cik[cik] for cik in sector_inventory_ciks)

                if sector_revenue == 0:
                    continue

                # Garde-fou anti-effondrement artificiel : si moins de la
                # moitié des entreprises du secteur ont publié leurs
                # inventaires ce trimestre-là (ex: trimestre le plus récent
                # pas encore totalement remonté dans EDGAR au moment du run),
                # on ignore ce point plutôt que d'afficher un ratio faussé
                # vers le bas -- sans ce garde-fou, TOUS les secteurs
                # s'effondrent artificiellement vers 0 sur les derniers
                # trimestres, simultanément, ce qui n'est pas un vrai
                # phénomène économique.
                min_coverage = max(1, len(ciks) // 2)
                if len(sector_inventory_ciks) < min_coverage:
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
    constituents = get_sp500_constituents()
    df = compute_inventory_to_sales(constituents=constituents)

    if df.empty:
        raise RuntimeError(
            "[12_inventory_to_sales_ratio] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_date = df["date"].max()
    sectors_present = sorted(df["sector"].unique())
    sector_colors = _sector_color_map(sectors_present)

    for sector in sectors_present:
        sub = df[df["sector"] == sector].sort_values("date")
        ax.plot(sub["date"], sub["inventory_to_sales_pct"], color=sector_colors[sector], linewidth=1.8,
                marker="o", markersize=3, label=sector)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Inventaires / CA annuel (%)", fontsize=9)
    ax.set_title("Ratio inventaires/ventes par secteur GICS",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)

    add_source_footer(
        fig,
        f"Source: SEC EDGAR (frames API) | Ratio = inventaires fin de trimestre / chiffre d'affaires TTM, "
        f"{len(constituents)} constituants S&P 500 (Wikipedia), secteurs GICS officiels",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "12_inventory_to_sales_ratio.png")

    finalize_chart(fig, ax, out_path, legend_ncol=4)

    print(f"[12_inventory_to_sales_ratio] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
