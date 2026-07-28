"""
Graphique : Marges opérationnelles par secteur

Source : SEC EDGAR, endpoint `frames`.

Concepts XBRL :
  - Revenus (fallback) : Revenues, RevenueFromContractWithCustomerExcludingAssessedTax, SalesRevenueNet
  - Résultat opérationnel : OperatingIncomeLoss

Méthode : pour chaque secteur GICS officiel (via common.sp500_list, qui va
chercher la vraie composition du S&P 500 sur Wikipedia), pour chaque
trimestre, on somme le résultat opérationnel et le chiffre d'affaires de
toutes les entreprises du secteur trouvées dans les données EDGAR ce
trimestre-là, on calcule chacun en TTM (glissant 12 mois, pour lisser la
saisonnalité -- ex: la distribution a un gros T4 chaque année), puis :

    marge_operationnelle = TTM_resultat_operationnel / TTM_revenus * 100

Pourquoi c'est utile : la compression ou l'expansion de marge sectorielle
révèle si le pricing power d'un secteur s'érode (marge qui baisse malgré
des revenus stables/en hausse) ou si un secteur isolé gagne en efficacité
opérationnelle -- une lecture agrégée que les chiffres d'une seule
entreprise ne permettent pas.

Sortie : PNG dans output/{periode}/11_sector_operating_margins.png
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
    add_freshness_subtitle
)
from common.config import get_current_period_label, OUTPUT_DIR, REVENUE_XBRL_CONCEPTS, OPERATING_INCOME_XBRL_CONCEPTS

# Fenêtre plus courte que HISTORY_YEARS : 11 secteurs GICS en détail
# trimestriel sur 10 ans deviendrait illisible : on se concentre sur les 5
# dernières années.
DISPLAY_YEARS = 5


def _sector_color_map(sectors: list) -> dict:
    """
    Génère une couleur distincte par secteur à partir d'une palette
    qualitative standard (tab20), indexée par ordre alphabétique des noms de
    secteurs réellement présents dans les données. Robuste si GICS ajoute,
    retire ou renomme un secteur un jour -- pas besoin de maintenir un
    dictionnaire de couleurs à la main par nom de secteur.
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
    transitoires (même logique que charts 09/10).
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


def compute_sector_margins(years: int = DISPLAY_YEARS, constituents: pd.DataFrame = None) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, secteur, operating_margin_pct.
    Récupère years+1 an de données brutes en plus (marge pour le calcul TTM).

    `constituents` : DataFrame optionnel (colonnes ticker, sector, cik) --
    si non fourni, va chercher la vraie composition actuelle du S&P 500
    (~500 entreprises, secteurs GICS officiels) via common.sp500_list.
    """
    if constituents is None:
        constituents = get_sp500_constituents()

    sector_ciks = {}
    for sector, group in constituents.groupby("sector"):
        sector_ciks[sector] = set(int(cik) for cik in group["cik"])

    current_year = datetime.today().year
    start_year = current_year - years - 1

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"

            revenue_by_cik = _get_merged_frame_for_period(REVENUE_XBRL_CONCEPTS, period)
            opinc_by_cik = _get_merged_frame_for_period(OPERATING_INCOME_XBRL_CONCEPTS, period)

            if not revenue_by_cik or not opinc_by_cik:
                continue

            quarter_end = _quarter_end_date(year, quarter)
            for sector, ciks in sector_ciks.items():
                sector_revenue = sum(v for cik, v in revenue_by_cik.items() if cik in ciks)
                sector_opinc = sum(v for cik, v in opinc_by_cik.items() if cik in ciks)
                if sector_revenue == 0:
                    continue
                records.append({
                    "date": quarter_end,
                    "sector": sector,
                    "revenue": sector_revenue,
                    "operating_income": sector_opinc,
                })

    df_long = pd.DataFrame(records)
    if df_long.empty:
        return df_long

    results = []
    for sector in df_long["sector"].unique():
        sub = df_long[df_long["sector"] == sector].sort_values("date").set_index("date")
        ttm_revenue = sub["revenue"].rolling(window=4).sum()
        ttm_opinc = sub["operating_income"].rolling(window=4).sum()
        margin = (ttm_opinc / ttm_revenue) * 100
        for date, val in margin.items():
            if pd.notna(val):
                results.append({"date": date, "sector": sector, "operating_margin_pct": val})

    margins_df = pd.DataFrame(results)
    if margins_df.empty:
        return margins_df

    date_min_display = margins_df["date"].max() - pd.DateOffset(years=years)
    return margins_df[margins_df["date"] >= date_min_display].reset_index(drop=True)


def generate():
    constituents = get_sp500_constituents()
    df = compute_sector_margins(constituents=constituents)

    if df.empty:
        raise RuntimeError(
            "[11_sector_operating_margins] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_date = df["date"].max()
    sectors_present = sorted(df["sector"].unique())
    sector_colors = _sector_color_map(sectors_present)

    for sector in sectors_present:
        sub = df[df["sector"] == sector].sort_values("date")
        ax.plot(sub["date"], sub["operating_margin_pct"], color=sector_colors[sector], linewidth=1.8,
                marker="o", markersize=3, label=sector)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Marge opérationnelle TTM (%)", fontsize=9)
    ax.set_title("Marges opérationnelles par secteur GICS (TTM)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=7, frameon=False, ncol=2)

    add_source_footer(
        fig,
        f"Source: SEC EDGAR (frames API) | Marge = résultat opérationnel TTM / chiffre d'affaires TTM, "
        f"{len(constituents)} constituants S&P 500 (Wikipedia), secteurs GICS officiels",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "11_sector_operating_margins.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[11_sector_operating_margins] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
