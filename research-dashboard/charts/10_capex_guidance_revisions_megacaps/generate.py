"""
Graphique : Accélération du capex des méga-caps (proxy de révision)

Source : SEC EDGAR, endpoint `frames` (comme les charts 09/11/12).

⚠️ CHANGEMENT DE MÉTHODE PAR RAPPORT AU PLAN INITIAL -- voir README de ce
dossier pour le détail. Le plan initial voulait extraire la guidance
textuelle ("nous prévoyons désormais un capex de X Md$") depuis les 10-Q/
communiqués de résultats via NLP/regex. C'est fragile et peu fiable dans la
durée (formulation différente à chaque boîte et chaque trimestre, aucune
donnée structurée disponible sur EDGAR pour ça). On utilise à la place une
"révision implicite" : l'accélération ou la décélération du capex RÉALISÉ
(TTM, glissant sur 12 mois) d'un trimestre à l'autre, par méga-cap. Ce n'est
pas une vraie révision de consensus analystes (qui nécessiterait une donnée
payante type FactSet/Visible Alpha), mais c'est le meilleur proxy gratuit et
fiable dans la durée.

Pourquoi c'est utile : une accélération du TTM d'un trimestre à l'autre
signale que l'entreprise dépense plus vite que sa propre tendance récente --
cohérent avec (même si pas identique à) une révision à la hausse de
guidance. C'est un signal correlé à ce que suivent les desks recherche
quand ils commentent les surprises de capex en saison de résultats.

Sortie : PNG dans output/{periode}/10_capex_guidance_revisions_megacaps.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, CAPEX_XBRL_CONCEPTS, MEGACAP_CAPEX_TICKERS

DISPLAY_YEARS = 3

LINE_COLORS = ["#1a3a5c", "#c0392b", "#2f6690", "#e08e79", "#5b8ab8", "#8fb8d8"]


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    """Retourne la date de fin du trimestre donné (dernier jour du mois)."""
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(period: str) -> dict:
    """
    Interroge tous les concepts XBRL candidats pour une période donnée,
    fusionne par CIK (même logique que chart 09 -- voir son README pour le
    détail du bug que ça corrige), et protège chaque appel individuellement
    contre les erreurs réseau transitoires.
    """
    combined = {}
    for concept in CAPEX_XBRL_CONCEPTS:
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


def compute_megacap_capex_ttm_growth(years: int = DISPLAY_YEARS, tickers: list = None) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, ticker, ttm_capex_billions, ttm_qoq_growth_pct.
    Récupère years+2 ans de données brutes (marge nécessaire pour calculer le
    TTM ET sa variation QoQ dès le premier trimestre affiché).
    """
    if tickers is None:
        tickers = MEGACAP_CAPEX_TICKERS

    ticker_to_cik = get_ticker_to_cik_map()
    cik_to_ticker = {}
    ciks = set()
    for t in tickers:
        cik = ticker_to_cik.get(t.upper())
        if cik is not None:
            cik_int = int(cik)
            ciks.add(cik_int)
            cik_to_ticker[cik_int] = t.upper()

    current_year = datetime.today().year
    start_year = current_year - years - 2

    records = []
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"
            combined = _get_merged_frame_for_period(period)
            if not combined:
                continue
            quarter_end = _quarter_end_date(year, quarter)
            for cik, value in combined.items():
                if cik not in ciks:
                    continue
                records.append({
                    "date": quarter_end,
                    "ticker": cik_to_ticker.get(cik, f"CIK{cik}"),
                    "capex_billions": value / 1e9,
                })

    df_long = pd.DataFrame(records)
    if df_long.empty:
        return df_long

    pivot = df_long.pivot_table(index="date", columns="ticker", values="capex_billions", aggfunc="sum")
    pivot = pivot.sort_index().fillna(0)

    ttm = pivot.rolling(window=4).sum()
    ttm_qoq_growth = ttm.pct_change(periods=1) * 100

    date_min_display = pivot.index.max() - pd.DateOffset(years=years)
    ttm_display = ttm[ttm.index >= date_min_display]
    growth_display = ttm_qoq_growth[ttm_qoq_growth.index >= date_min_display]

    result = []
    for ticker in pivot.columns:
        for date in ttm_display.index:
            ttm_val = ttm_display.loc[date, ticker]
            growth_val = growth_display.loc[date, ticker] if date in growth_display.index else None
            result.append({
                "date": date,
                "ticker": ticker,
                "ttm_capex_billions": ttm_val,
                "ttm_qoq_growth_pct": growth_val,
            })

    return pd.DataFrame(result)


def generate():
    df = compute_megacap_capex_ttm_growth()

    if df.empty:
        raise RuntimeError(
            "[10_capex_guidance_revisions_megacaps] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    df = df.dropna(subset=["ttm_qoq_growth_pct"])
    if df.empty:
        raise RuntimeError(
            "[10_capex_guidance_revisions_megacaps] Pas assez d'historique pour calculer "
            "la croissance TTM QoQ sur la fenêtre d'affichage."
        )

    fig, ax = setup_figure()

    last_date = df["date"].max()
    tickers_present = sorted(df["ticker"].unique())

    for i, ticker in enumerate(tickers_present):
        sub = df[df["ticker"] == ticker].sort_values("date")
        color = LINE_COLORS[i % len(LINE_COLORS)]
        ax.plot(sub["date"], sub["ttm_qoq_growth_pct"], color=color, linewidth=1.8, marker="o",
                markersize=3, label=ticker)

    ax.axhline(0, color="#999999", linewidth=0.8)
    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Croissance du TTM capex, QoQ (%)", fontsize=9)
    ax.set_title("Accélération du capex des méga-caps (proxy de révision)",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=2)

    add_source_footer(
        fig,
        "Source: SEC EDGAR (frames API) | Variation trimestrielle du capex annualisé (TTM) -- "
        "proxy de révision, pas un consensus analystes",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "10_capex_guidance_revisions_megacaps.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[10_capex_guidance_revisions_megacaps] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
