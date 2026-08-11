"""
Graphique : Inscriptions hebdomadaires au chômage (initial jobless claims).

Série FRED :
  - ICSA : nouvelles demandes d'allocations chômage, hebdomadaire,
           désaisonnalisé, en personnes. Publiée chaque jeudi pour la
           semaine close le samedi précédent -- la donnée macro la plus
           rapide qui existe.

Calcul : série brute en trait fin + moyenne mobile 4 semaines (la lecture
standard, qui gomme le bruit des jours fériés) en trait principal.

Pourquoi c'est utile : les claims se retournent AVANT le taux de chômage --
c'est l'indicateur avancé de notre indicateur avancé (la règle de Sahm,
chart 02). Une dérive soutenue de la MA4 au-dessus de ses plus bas est
historiquement le premier signal dur de retournement du marché du travail,
des mois avant que le taux de chômage ne bouge.

Sortie : PNG dans output/{periode}/31_initial_jobless_claims.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, mark_last_point, format_last_value_label,
    finalize_chart, COLOR_ACCENT, COLOR_THIRD,
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

# Garde-fou : jamais moins de ~150k même au plus fort d'un boom, pic COVID
# ~6.1M -- une valeur hors de [50k, 10M] est une erreur de données.
PLAUSIBLE_RANGE = (50_000, 10_000_000)


def compute_claims(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """Retourne un DataFrame: date, claims, ma4 (en milliers de personnes)."""
    raw = get_series("ICSA", years=years)
    raw = raw.rename(columns={"value": "claims"}).sort_values("date").reset_index(drop=True)

    lo, hi = PLAUSIBLE_RANGE
    if not raw["claims"].between(lo, hi).all():
        bad = raw.loc[~raw["claims"].between(lo, hi), "claims"].iloc[0]
        raise RuntimeError(
            f"[31_initial_jobless_claims] Valeur ICSA implausible ({bad:,.0f} personnes, "
            f"attendu dans [{lo:,} ; {hi:,}]) -- unité ou série FRED à re-vérifier."
        )

    raw["claims"] = raw["claims"] / 1000.0  # en milliers, plus lisible
    raw["ma4"] = raw["claims"].rolling(4).mean()
    return raw.dropna(subset=["ma4"]).reset_index(drop=True)


def generate():
    df = compute_claims()

    if df.empty:
        raise RuntimeError(
            "[31_initial_jobless_claims] Aucune donnée récupérée depuis FRED (ICSA). "
            "Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]

    line_raw, = ax.plot(df["date"], df["claims"], color=COLOR_THIRD, linewidth=0.8,
                        alpha=0.75, label="Hebdomadaire (brut)", zorder=2)
    line_ma4, = ax.plot(df["date"], df["ma4"], color=COLOR_ACCENT, linewidth=1.9,
                        label=format_last_value_label(
                            "Moyenne 4 semaines", f"{last_row['ma4']:,.0f}k".replace(",", " "),
                            series=df["ma4"], years_label=f"{HISTORY_YEARS} ans"),
                        zorder=3)
    mark_last_point(ax, last_row["date"], last_row["ma4"])

    # Échelle log : le pic COVID (~6 100k) écraserait sinon toute la
    # variation "normale" de la série (150k-450k), qui est précisément là où
    # vivent les signaux -- avec 10 ans de fenêtre glissante, ce pic restera
    # dans le champ jusqu'en 2030.
    ax.set_yscale("log")
    # Graduations explicites + formateurs "plats" sur les axes majeur ET
    # mineur : les formateurs log par défaut de matplotlib émettent du
    # mathtext ($10^{3}$...), que le projet désactive globalement
    # (text.parse_math=False dans chart_style) -- sans ceci, les étiquettes
    # s'affichent comme du code brut.
    from matplotlib.ticker import ScalarFormatter, FixedLocator, NullFormatter, NullLocator
    ax.yaxis.set_major_locator(FixedLocator([200, 300, 500, 1000, 2000, 4000]))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_formatter(NullFormatter())

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Milliers de personnes / semaine (éch. log)", fontsize=9)
    ax.set_title("Marché du travail en temps réel : inscriptions hebdomadaires au chômage",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (ICSA, US Employment and Training Administration) | Hebdomadaire, "
        "désaisonnalisé | Échelle logarithmique (pic COVID ~6 100k)",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "31_initial_jobless_claims.png")

    finalize_chart(fig, ax, out_path, handles=[line_ma4, line_raw])

    print(f"[31_initial_jobless_claims] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
