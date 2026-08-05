"""
Graphique : Capex trimestriel par principaux contributeurs (3 dernières
années) + tendance annuelle (TTM)

Source : SEC EDGAR, endpoint `frames` (un concept XBRL donné, pour TOUTES
les entreprises, sur un trimestre donné, en un seul appel API).

Contrairement à la première version (capex agrégé total sur 10 ans), ce
chart se concentre sur les 3 dernières années en détail trimestriel, avec :
  1. Une décomposition par entreprise (barres empilées) pour voir QUI tire
     le capex agrégé -- typiquement dominé par une poignée d'hyperscalers
  2. Une ligne de tendance annuelle (somme glissante sur 12 mois, "TTM")
     superposée, pour lisser le bruit trimestriel et voir la dynamique
     annuelle sous-jacente

Concepts XBRL essayés dans l'ordre (fallback) -- voir common/config.py :
  - PaymentsToAcquirePropertyPlantAndEquipment
  - PaymentsForCapitalImprovements
  - PaymentsToAcquireProductiveAssets

Pourquoi c'est utile : le capex agrégé total (version précédente) ne dit pas
qui pousse la tendance. Avec l'explosion des dépenses d'infrastructure IA,
savoir si la hausse vient de 3-4 hyperscalers ou d'une base large
d'entreprises change complètement l'interprétation du signal macro.

Sortie : PNG dans output/{periode}/09_capex_sp500_aggregate.png
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
    finalize_chart, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, CAPEX_XBRL_CONCEPTS

# Ce chart se concentre volontairement sur une fenêtre plus courte que les
# autres (3 ans au lieu de 10) pour rester lisible en détail trimestriel
# avec une décomposition par entreprise.
DISPLAY_YEARS = 3
TOP_N = 6

# Palette pour les entreprises + "Autres" (dernière couleur = Autres, gris neutre)
BAR_COLORS = ["#1a3a5c", "#2f6690", "#5b8ab8", "#8fb8d8", "#c0392b", "#e08e79", "#bbbbbb"]
COLOR_TTM_LINE = "#222222"


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    """Retourne la date de fin du trimestre donné (dernier jour du mois)."""
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(period: str) -> dict:
    """
    Interroge TOUS les concepts XBRL candidats pour une période donnée et
    fusionne les résultats par CIK (au lieu de s'arrêter au premier concept
    qui renvoie des données pour N'IMPORTE QUELLE entreprise).

    Bug corrigé (1) : l'ancienne version prenait le PREMIER concept renvoyant
    des données globalement, puis abandonnait les autres concepts pour cette
    période -- ce qui excluait silencieusement, sur TOUTE la fenêtre, toute
    entreprise taguant son capex avec un concept différent du premier trouvé
    (ex: si Amazon ou Apple utilisent un tag XBRL différent de
    PaymentsToAcquirePropertyPlantAndEquipment, ils disparaissaient
    entièrement du graphique sans aucun message d'erreur).

    Bug corrigé (2) : une erreur réseau ponctuelle (timeout, erreur serveur
    transitoire côté SEC) sur UN SEUL appel concept/trimestre faisait planter
    tout le graphique. Chaque appel est maintenant protégé individuellement :
    un échec est juste signalé et ignoré, sans interrompre le reste du calcul.

    Retourne un dict {cik: value}, en préférant la valeur du premier concept
    de la liste si une entreprise est présente dans plusieurs concepts.
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
            if cik not in combined:  # le premier concept trouvé pour ce CIK gagne
                combined[cik] = row["value"]
    return combined


def compute_capex_by_company(years: int = DISPLAY_YEARS, constituents: pd.DataFrame = None) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, ticker, capex_billions.
    Récupère `years + 1` ans de données (l'année en plus sert uniquement à
    pouvoir calculer la tendance annuelle glissante -- TTM -- dès le premier
    trimestre affiché).

    `constituents` : DataFrame optionnel (colonnes ticker, cik) -- si non
    fourni, va chercher la vraie composition actuelle du S&P 500 (~500
    entreprises) via common.sp500_list, pas un échantillon.
    """
    if constituents is None:
        constituents = get_sp500_constituents()

    cik_to_ticker = {}
    ciks = set()
    for _, row in constituents.iterrows():
        cik_int = int(row["cik"])
        ciks.add(cik_int)
        # En cas de double classe d'actions (ex: GOOGL/GOOG, même CIK), on
        # garde le premier ticker rencontré pour l'affichage -- l'agrégat
        # financier est de toute façon le même pour les deux classes.
        cik_to_ticker.setdefault(cik_int, row["ticker"])

    current_year = datetime.today().year
    start_year = current_year - years - 1  # +1 an de marge pour le calcul TTM

    # Premier passage : on collecte tout, en gardant trace du nombre
    # d'entreprises effectivement trouvées par trimestre (sur nos ~500
    # constituants), pour pouvoir repérer les trimestres pas encore
    # complètement remontés dans EDGAR au moment du run.
    raw_by_quarter = {}  # quarter_end -> {cik: value}
    for year in range(start_year, current_year + 1):
        for quarter in [1, 2, 3, 4]:
            period = f"CY{year}Q{quarter}"
            combined = _get_merged_frame_for_period(period)
            if not combined:
                continue
            matched = {cik: v for cik, v in combined.items() if cik in ciks}
            if matched:
                raw_by_quarter[_quarter_end_date(year, quarter)] = matched

    if not raw_by_quarter:
        return pd.DataFrame()

    # Garde-fou anti-effondrement artificiel (même logique que chart 12) :
    # un trimestre où beaucoup moins d'entreprises ont publié que la normale
    # est presque toujours un trimestre pas encore complètement remonté dans
    # EDGAR au moment du run (pas un vrai effondrement du capex). On l'exclut
    # plutôt que d'afficher un total faussé vers le bas.
    #
    # Important : le seuil se base sur la MÉDIANE de couverture, pas le
    # maximum. Sur les ~500 constituants du S&P 500, un seul trimestre par an
    # concentre souvent une couverture anormalement élevée (le calendrier
    # fiscal fait qu'un trimestre civil capte plus de dépôts 10-K annuels que
    # les autres) -- un seuil basé sur ce pic exclurait à tort la majorité des
    # trimestres pourtant parfaitement valides.
    coverage_counts = [len(v) for v in raw_by_quarter.values()]
    median_coverage = pd.Series(coverage_counts).median()
    min_coverage = max(1, int(median_coverage * 0.5))

    records = []
    for quarter_end, matched in raw_by_quarter.items():
        if len(matched) < min_coverage:
            continue
        for cik, value in matched.items():
            records.append({
                "date": quarter_end,
                "ticker": cik_to_ticker.get(cik, f"CIK{cik}"),
                "capex_billions": value / 1e9,
            })

    return pd.DataFrame(records)


def _build_pivot_and_ttm(df_long: pd.DataFrame, years: int, top_n: int):
    """
    Transforme le DataFrame long en table pivot (date x ticker), calcule le
    TTM (somme glissante 4 trimestres) sur la fenêtre étendue, puis restreint
    tout à la fenêtre d'affichage réelle (`years`).

    Retourne (pivot_display, ttm_display, top_tickers).
    """
    pivot = df_long.pivot_table(index="date", columns="ticker", values="capex_billions", aggfunc="sum")
    pivot = pivot.sort_index().fillna(0)

    # TTM calculé sur la fenêtre ÉTENDUE (avant de couper), pour que le
    # premier trimestre affiché ait bien 4 trimestres d'historique derrière lui.
    total_per_quarter = pivot.sum(axis=1)
    ttm = total_per_quarter.rolling(window=4).sum()

    # Fenêtre d'affichage réelle : les derniers `years` ans seulement
    date_min_display = pivot.index.max() - pd.DateOffset(years=years)
    pivot_display = pivot[pivot.index >= date_min_display]
    ttm_display = ttm[ttm.index >= date_min_display]

    # Top N contributeurs sur la fenêtre affichée (pas la fenêtre étendue)
    totals_by_ticker = pivot_display.sum(axis=0).sort_values(ascending=False)
    top_tickers = list(totals_by_ticker.head(top_n).index)

    return pivot_display, ttm_display, top_tickers


def generate():
    constituents = get_sp500_constituents()
    df_long = compute_capex_by_company(constituents=constituents)

    if df_long.empty:
        raise RuntimeError(
            "[09_capex_sp500_aggregate] Aucune donnée récupérée depuis EDGAR frames. "
            "Vérifie EDGAR_USER_AGENT et la connectivité réseau vers data.sec.gov / sec.gov."
        )

    pivot, ttm, top_tickers = _build_pivot_and_ttm(df_long, DISPLAY_YEARS, TOP_N)

    if pivot.empty:
        raise RuntimeError(
            "[09_capex_sp500_aggregate] Pas assez de données sur la fenêtre d'affichage "
            f"({DISPLAY_YEARS} ans) pour générer le graphique."
        )

    other_tickers = [t for t in pivot.columns if t not in top_tickers]
    pivot["Autres"] = pivot[other_tickers].sum(axis=1) if other_tickers else 0.0
    plot_columns = top_tickers + ["Autres"]

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)

    # Barres empilées : une couleur par contributeur principal + gris pour "Autres"
    bottom = pd.Series(0.0, index=pivot.index)
    bar_width = 70  # jours, adapté à un espacement trimestriel
    bars_for_legend = []
    for i, col in enumerate(plot_columns):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        bar = ax.bar(pivot.index, pivot[col], bottom=bottom, width=bar_width,
                      color=color, label=col, zorder=3)
        bars_for_legend.append(bar)
        bottom = bottom + pivot[col]

    # Tendance annuelle (TTM) superposée sur l'axe secondaire. La dernière
    # valeur TTM est portée par le label de légende (pas de texte dans la
    # zone de tracé -- règle du projet, voir chart_style.finalize_chart).
    ttm_clean = ttm.dropna()
    ttm_label = "Tendance annuelle (TTM, éch. droite)"
    if not ttm_clean.empty:
        ttm_label += f" : {ttm_clean.iloc[-1]:.0f} Md$"
    line_ttm, = ax2.plot(ttm.index, ttm.values, color=COLOR_TTM_LINE, linewidth=2.0,
                          marker="o", markersize=4, label=ttm_label, zorder=5)

    last_date = pivot.index.max()
    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Capex trimestriel (Milliards USD)", fontsize=9)
    ax2.set_ylabel("Capex annuel glissant -- TTM (Milliards USD)", fontsize=9, color=COLOR_TTM_LINE)
    ax2.tick_params(colors=COLOR_TTM_LINE, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title(f"Capex par principal contributeur — {DISPLAY_YEARS} dernières années",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)

    last_total = pivot.loc[last_date, plot_columns].sum()

    add_source_footer(
        fig,
        f"Source: SEC EDGAR (frames API) | Top {TOP_N} contributeurs sur les {len(constituents)} "
        f"constituants du S&P 500 (Wikipedia, mis à jour à chaque run)",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "09_capex_sp500_aggregate.png")

    handles = [b[0] for b in bars_for_legend] + [line_ttm]
    labels = plot_columns + [line_ttm.get_label()]
    finalize_chart(fig, ax, out_path, handles=handles, labels=labels, legend_ncol=4,
                   note=f"Dernier trimestre : {last_total:.0f} Md$ de capex agrégé")

    print(f"[09_capex_sp500_aggregate] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
