"""
Graphique : Positionnement spéculatif (CFTC COT) -- S&P 500, T-Note 10 ans, Dollar

Source : CFTC Public Reporting Environment (API Socrata officielle,
gratuite, sans clé), dataset "Legacy - Futures Only". Voir
common/cftc_client.py pour les détails (codes de contrats stables,
rate limiting, cache incrémental).

Contrats suivis (common.config.COT_CONTRACTS) :
  - E-mini S&P 500 (code 13874A)
  - T-Note 10 ans (code 043602)
  - Dollar Index ICE (code 098662)

Métrique : position nette des non-commercials (spéculateurs) en % de
l'open interest -- normalisation indispensable pour comparer les contrats
entre eux et dans le temps (voir cftc_client).

Pourquoi c'est utile : les prix disent ce que le marché pense, le COT dit
ce qu'il a déjà FAIT. Un consensus déjà tout positionné n'a plus
d'acheteurs marginaux : les extrêmes de positionnement spéculatif sont des
signaux contrariens classiques, et les retournements violents (short
squeeze sur les Treasuries, débouclage de shorts dollar...) partent
presque toujours d'un positionnement extrême. C'est l'angle mort le plus
net d'un pack construit uniquement sur les prix : aucun autre graphique du
rapport ne dit "qui est déjà dans le trade".

Sortie : PNG dans output/{periode}/27_cot_positioning.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.cftc_client import get_cot_net_positioning
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, mark_last_point, format_last_value_label,
    finalize_chart, COLOR_ACCENT, COLOR_SECOND, COLOR_THIRD
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS, COT_CONTRACTS

CONTRACT_COLORS = [COLOR_ACCENT, COLOR_SECOND, COLOR_THIRD]


def compute_cot_positioning(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame long: date, contract, net_pct_oi.
    Chaque contrat est récupéré indépendamment et protégé contre les
    erreurs réseau : un contrat indisponible est signalé et ignoré, les
    autres restent tracés (même philosophie que les charts EDGAR).
    """
    frames = []
    for name, code in COT_CONTRACTS.items():
        try:
            df = get_cot_net_positioning(code, years=years)
        except Exception as e:
            print(f"  [avertissement] échec CFTC pour {name} ({code}): {e} -- ignoré, on continue")
            continue
        if df.empty:
            print(f"  [avertissement] aucune donnée CFTC pour {name} ({code}) -- "
                  "code de contrat à vérifier sur publicreporting.cftc.gov")
            continue
        df = df.rename(columns={"value": "net_pct_oi"})
        df["contract"] = name
        frames.append(df[["date", "contract", "net_pct_oi"]])

    if not frames:
        return pd.DataFrame(columns=["date", "contract", "net_pct_oi"])
    return pd.concat(frames, ignore_index=True).sort_values("date").reset_index(drop=True)


def generate():
    df = compute_cot_positioning()

    if df.empty:
        raise RuntimeError(
            "[27_cot_positioning] Aucune donnée récupérée depuis l'API CFTC "
            "(publicreporting.cftc.gov). Vérifie la connectivité réseau, et si le "
            "problème persiste, les codes de contrats dans common/config.py::COT_CONTRACTS."
        )

    # Garde-fou de vraisemblance : une position nette en % de l'open interest
    # est bornée par construction dans [-100, 100]. Au-delà, le calcul ou les
    # colonnes de l'API ont changé -- échouer plutôt que publier un non-sens.
    if df["net_pct_oi"].abs().max() > 100:
        raise RuntimeError(
            "[27_cot_positioning] Position nette > 100% de l'open interest -- "
            "impossible par construction. Le schéma de l'API CFTC a probablement "
            "changé, vérifier les colonnes dans common/cftc_client.py."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_date = df["date"].max()
    for i, name in enumerate(COT_CONTRACTS):
        sub = df[df["contract"] == name].sort_values("date")
        if sub.empty:
            continue
        color = CONTRACT_COLORS[i % len(CONTRACT_COLORS)]
        last = sub.iloc[-1]
        ax.plot(sub["date"], sub["net_pct_oi"], color=color, linewidth=1.6,
                label=format_last_value_label(name, f"{last['net_pct_oi']:+.1f}% OI",
                                              series=sub["net_pct_oi"],
                                              years_label=f"{HISTORY_YEARS} ans"))
        mark_last_point(ax, last["date"], last["net_pct_oi"], color=color)

    # Zéro : au-dessus, les spéculateurs sont nets acheteurs
    ax.axhline(0, color="#555555", linewidth=0.9, linestyle="--", zorder=1)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Position nette des spéculateurs (% de l'open interest)", fontsize=9)
    ax.set_title("Positionnement spéculatif (CFTC COT) : actions, taux, dollar",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)

    add_source_footer(
        fig,
        "Source: CFTC Commitments of Traders (Legacy Futures Only, publicreporting.cftc.gov) | "
        "Net non-commercials / open interest. Les percentiles signalent les extrêmes de "
        "positionnement -- lecture contrarienne",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "27_cot_positioning.png")

    finalize_chart(fig, ax, out_path, legend_ncol=1)

    print(f"[27_cot_positioning] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
