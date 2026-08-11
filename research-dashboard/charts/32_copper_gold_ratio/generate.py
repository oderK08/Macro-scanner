"""
Graphique : Ratio cuivre/or vs taux 10 ans US -- la croissance vue par
les matières premières.

Sources :
  - FRED PCOPPUSDM : prix mondial du cuivre (FMI, Primary Commodity
                     Prices), $/tonne métrique, mensuel
  - DBnomics IMF/PCPS : prix mondial de l'or ($/once troy, mensuel) --
                        l'or n'est pas disponible sur FRED (les séries LBMA
                        en ont été retirées pour raison de licence), mais
                        le FMI le publie dans la même base PCPS que le
                        cuivre, republiée par DBnomics sans clé API
  - FRED DGS10 : taux 10 ans US, quotidien (moyenné par mois ici)

⚠️ La partie DBnomics (or) n'a pas pu être testée en conditions réelles au
moment de l'écriture : premier run à valider, comme les charts 15/27/29.
La série est cherchée par texte libre + code "PGOLD", pas par identifiant
complet figé.

Pourquoi c'est utile : le classique de Gundlach. Le cuivre price la
croissance industrielle mondiale, l'or price la peur et les taux réels --
leur ratio est un "vote" des matières premières sur la croissance
nominale, qui suit remarquablement le taux 10 ans US. Quand le ratio et le
taux divergent, l'un des deux marchés se trompe : c'est la divergence qui
fait le signal, et aucun autre chart du rapport ne fait parler les
matières premières.

Sortie : PNG dans output/{periode}/32_copper_gold_ratio.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.dbnomics_client import search_series, get_series_observations
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, mark_last_point, format_last_value_label,
    finalize_chart, COLOR_ACCENT, COLOR_BENCHMARK,
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

PROVIDER = "IMF"
DATASET = "PCPS"

# Garde-fous. Ordres de grandeur : cuivre ~8 000-11 000 $/t, or
# ~2 000-3 500 $/oz -> ratio ~2.5-5. Des bornes larges pour absorber des
# régimes de prix futurs très différents, mais qui attrapent une erreur
# d'unité (le cuivre est parfois coté en cents/livre : facteur ~45).
COPPER_PLAUSIBLE_USD_MT = (1_000, 50_000)
GOLD_PLAUSIBLE_USD_OZ = (500, 20_000)
RATIO_PLAUSIBLE = (0.2, 20)
YIELD_PLAUSIBLE_PCT = (-2, 25)


def _get_gold_series() -> pd.DataFrame:
    """
    Récupère le prix mensuel de l'or ($/oz) depuis DBnomics (IMF/PCPS).
    Recherche par texte libre, filtrée sur le code commodity PGOLD et une
    périodicité mensuelle -- pas d'identifiant complet codé en dur.
    """
    docs = search_series(PROVIDER, DATASET, "gold price US dollars", limit=30)
    for doc in docs:
        code = doc.get("series_code", "")
        name = doc.get("series_name", "").lower()
        if "PGOLD" in code and code.startswith("M.") and "gold" in name:
            obs = get_series_observations(PROVIDER, DATASET, code)
            print(f"[32_copper_gold_ratio] Or: OK via {code}")
            return obs
    raise RuntimeError(
        "[32_copper_gold_ratio] Aucune série d'or mensuelle (PGOLD) trouvée dans "
        "IMF/PCPS via DBnomics -- le schéma de codes du dataset a peut-être changé, "
        f"codes vus: {[d.get('series_code') for d in docs[:5]]}"
    )


def compute_copper_gold_vs_yield(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame mensuel: date, ratio, yield_10y."""
    copper = get_series("PCOPPUSDM", years=years)
    copper = copper.rename(columns={"value": "copper"}).sort_values("date")

    gold = _get_gold_series().rename(columns={"value": "gold"}).sort_values("date")
    date_min = copper["date"].min()
    gold = gold[gold["date"] >= date_min - pd.Timedelta(days=45)]

    lo, hi = COPPER_PLAUSIBLE_USD_MT
    if not copper["copper"].between(lo, hi).all():
        bad = copper.loc[~copper["copper"].between(lo, hi), "copper"].iloc[0]
        raise RuntimeError(
            f"[32_copper_gold_ratio] Prix du cuivre implausible ({bad:,.0f} $/t, attendu "
            f"dans [{lo:,} ; {hi:,}]) -- unité de PCOPPUSDM à re-vérifier."
        )
    lo, hi = GOLD_PLAUSIBLE_USD_OZ
    if not gold["gold"].between(lo, hi).all():
        bad = gold.loc[~gold["gold"].between(lo, hi), "gold"].iloc[0]
        raise RuntimeError(
            f"[32_copper_gold_ratio] Prix de l'or implausible ({bad:,.0f} $/oz, attendu "
            f"dans [{lo:,} ; {hi:,}]) -- la série DBnomics n'est probablement pas en $/once."
        )

    merged = pd.merge_asof(copper, gold[["date", "gold"]], on="date",
                           direction="nearest", tolerance=pd.Timedelta(days=20))
    merged["ratio"] = merged["copper"] / merged["gold"]

    y10 = get_series("DGS10", years=years).rename(columns={"value": "yield_10y"})
    y10_monthly = (y10.set_index("date")["yield_10y"]
                   .resample("MS").mean().reset_index())

    merged = pd.merge_asof(merged.sort_values("date"), y10_monthly.sort_values("date"),
                           on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=20))
    return merged.dropna(subset=["ratio", "yield_10y"]).reset_index(drop=True)


def generate():
    df = compute_copper_gold_vs_yield()

    if df.empty:
        raise RuntimeError(
            "[32_copper_gold_ratio] Aucune donnée exploitable (FRED PCOPPUSDM/DGS10 "
            "ou DBnomics IMF/PCPS). Vérifie les connectivités réseau."
        )

    lo, hi = RATIO_PLAUSIBLE
    if not df["ratio"].between(lo, hi).all():
        bad = df.loc[~df["ratio"].between(lo, hi), "ratio"].iloc[0]
        raise RuntimeError(
            f"[32_copper_gold_ratio] Ratio cuivre/or implausible ({bad:.2f}, attendu dans "
            f"[{lo}, {hi}]) -- les unités des deux prix ne sont plus cohérentes entre elles."
        )
    lo, hi = YIELD_PLAUSIBLE_PCT
    if not df["yield_10y"].between(lo, hi).all():
        raise RuntimeError(
            "[32_copper_gold_ratio] Taux 10 ans hors de la plage plausible -- série DGS10 "
            "à re-vérifier."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]

    line_ratio, = ax.plot(df["date"], df["ratio"], color=COLOR_ACCENT, linewidth=1.9,
                          label=format_last_value_label(
                              "Cuivre/or (éch. gauche)", f"{last_row['ratio']:.2f}",
                              series=df["ratio"], years_label=f"{HISTORY_YEARS} ans"),
                          zorder=3)
    line_yield, = ax2.plot(df["date"], df["yield_10y"], color=COLOR_BENCHMARK,
                           linewidth=1.2, linestyle="--",
                           label=format_last_value_label(
                               "Taux 10 ans US (%, éch. droite)",
                               f"{last_row['yield_10y']:.2f}%"),
                           zorder=2)
    mark_last_point(ax, last_row["date"], last_row["ratio"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Ratio cuivre ($/t) / or ($/oz)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Taux 10 ans (%)", fontsize=9, color="#888888")
    ax2.tick_params(colors="#888888", labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("La croissance vue par les métaux : ratio cuivre/or vs taux 10 ans",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (PCOPPUSDM, DGS10) et DBnomics (IMF/PCPS, or) | Prix mondiaux FMI, "
        "mensuels ; taux 10 ans moyenné par mois | Cuivre = croissance, or = peur : la "
        "divergence avec le taux fait le signal",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "32_copper_gold_ratio.png")

    finalize_chart(fig, ax, out_path, handles=[line_ratio, line_yield])

    print(f"[32_copper_gold_ratio] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
