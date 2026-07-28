"""
Graphique : Capex agrégé (échantillon de grandes capitalisations US)

Source : SEC EDGAR, endpoint `frames` (un concept XBRL donné, pour TOUTES
les entreprises, sur un trimestre donné, en un seul appel API).

Concepts XBRL essayés dans l'ordre (fallback) -- voir common/config.py :
  - PaymentsToAcquirePropertyPlantAndEquipment
  - PaymentsForCapitalImprovements
  - PaymentsToAcquireProductiveAssets

Méthode : pour chaque trimestre des N dernières années, on récupère le
concept capex pour TOUTES les entreprises via `frames`, on filtre sur les
CIK correspondant à notre échantillon de grandes capitalisations
(common.config.SP500_LARGE_CAP_SAMPLE), puis on somme.

Pourquoi c'est utile : le capex agrégé des grandes entreprises US est un
indicateur avancé du cycle d'investissement -- particulièrement suivi
actuellement avec l'explosion des dépenses d'infrastructure IA chez les
hyperscalers (Microsoft, Meta, Amazon, Google).

Sortie : PNG dans output/{periode}/09_capex_sp500_aggregate.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis,
    add_freshness_subtitle, highlight_last_point, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS, CAPEX_XBRL_CONCEPTS, SP500_LARGE_CAP_SAMPLE


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    """Retourne la date de fin du trimestre donné (dernier jour du mois)."""
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def compute_capex_aggregate(years: int = HISTORY_YEARS, tickers: list = None) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, capex_total_billions, n_companies.
    Interroge l'endpoint EDGAR `frames` trimestre par trimestre sur la
    fenêtre demandée, filtre sur les CIK de `tickers`, et agrège.
    """
    if tickers is None:
        tickers = SP500_LARGE_CAP_SAMPLE

    ticker_to_cik = get_ticker_to_cik_map()
    ciks = set()
    for t in tickers:
        cik = ticker_to_cik.get(t.upper())
        if cik is not None:
            ciks.add(int(cik))

    current_year = datetime.today().year
    start_year = current_year - years

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"

            frame_df = pd.DataFrame()
            for concept in CAPEX_XBRL_CONCEPTS:
                frame_df = get_frame(concept, period)
                if not frame_df.empty:
                    break

            if frame_df.empty:
                continue

            frame_df = frame_df.copy()
            frame_df["cik"] = frame_df["cik"].astype(int)
            filtered = frame_df[frame_df["cik"].isin(ciks)]

            if filtered.empty:
                continue

            records.append({
                "date": _quarter_end_date(year, quarter),
                "capex_total_billions": filtered["value"].sum() / 1e9,
                "n_companies": filtered["cik"].nunique(),
            })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df = df.sort_values("date").reset_index(drop=True)

    # On ne garde que les trimestres avec une couverture minimale (au moins
    # la moitié des tickers suivis ont publié) pour éviter des faux creux
    # liés à des données pas encore disponibles au moment du run.
    min_companies = max(1, len(tickers) // 2)
    df = df[df["n_companies"] >= min_companies].reset_index(drop=True)
    return df


def generate():
    df = compute_capex_aggregate()

    if df.empty:
        raise RuntimeError(
            "[09_capex_sp500_aggregate] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    fig, ax = setup_figure()

    ax.plot(df["date"], df["capex_total_billions"], color=COLOR_ACCENT, linewidth=2.0, marker="o",
            markersize=3, label=f"Capex trimestriel agrégé ({len(SP500_LARGE_CAP_SAMPLE)} grandes capitalisations)")

    last_row = df.iloc[-1]
    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Milliards USD", fontsize=9)
    ax.set_title("Capex agrégé — échantillon de grandes capitalisations US",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    highlight_last_point(
        ax, last_row["date"], last_row["capex_total_billions"],
        value_label=f"${last_row['capex_total_billions']:.0f}Md ({int(last_row['n_companies'])} entreprises)",
    )

    add_source_footer(
        fig,
        f"Source: SEC EDGAR (frames API) | Échantillon de {len(SP500_LARGE_CAP_SAMPLE)} grandes capitalisations, pas l'indice S&P 500 complet",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "09_capex_sp500_aggregate.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[09_capex_sp500_aggregate] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
