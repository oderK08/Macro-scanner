"""
Graphique : Charge d'intérêts fédérale en % des recettes de l'État US

Séries FRED (données BEA, comptes nationaux NIPA) :
  - A091RC1Q027SBEA : dépenses d'intérêts du gouvernement fédéral,
                       trimestriel, milliards de $ (rythme annualisé, SAAR)
  - FGRECPT          : recettes courantes du gouvernement fédéral,
                       trimestriel, milliards de $ (rythme annualisé, SAAR)

Calcul :
    charge_interets_pct = intérêts / recettes * 100

Les deux séries sont dans la même unité et la même convention (SAAR) --
le ratio est donc directement interprétable, sans conversion.

Choix de source : ces données existent aussi via l'API FiscalData du
Trésor (comptabilité budgétaire), mais les séries NIPA équivalentes sont
sur FRED -- client déjà en place, cache déjà géré, une source de panne en
moins. La nuance comptable (NIPA vs budgétaire) ne change pas l'histoire
que raconte le ratio.

Fenêtre : 25 ans, volontairement plus longue que les 10 ans standard du
projet. La question de ce chart est un changement de RÉGIME budgétaire --
il faut voir les années 1990-2000 (charge >15% puis vingt ans de détente
par la baisse des taux) pour juger si le niveau actuel est une
normalisation ou une rupture. Sur 10 ans, le chart ne montrerait qu'une
hausse sans point de comparaison.

Pourquoi c'est utile : c'est LA question de dominance budgétaire qu'un
comité doit suivre depuis 2023 -- quelle part des recettes de l'État part
en intérêts avant toute dépense ? Plus ce ratio monte, plus la politique
budgétaire est contrainte, plus la tentation de tolérer l'inflation ou de
peser sur la Fed est forte, et plus l'offre d'obligations pèse sur le term
premium (chart 07) et le dollar (chart 20).

Sortie : PNG dans output/{periode}/26_federal_interest_burden.png
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
    finalize_chart, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR

# Fenêtre longue assumée : l'objet du chart est un changement de régime
# budgétaire, illisible sur les 10 ans standard (voir docstring).
DISPLAY_YEARS = 25


def compute_interest_burden(years: int = DISPLAY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, interest_pct_receipts.
    Les deux séries sont trimestrielles, publiées aux mêmes dates (comptes
    nationaux BEA) -> merge_asof avec petite tolérance par sécurité.
    """
    interest = get_series("A091RC1Q027SBEA", years=years)
    receipts = get_series("FGRECPT", years=years)

    interest = interest.rename(columns={"value": "interest"}).sort_values("date")
    receipts = receipts.rename(columns={"value": "receipts"}).sort_values("date")

    merged = pd.merge_asof(interest, receipts, on="date", direction="nearest",
                           tolerance=pd.Timedelta(days=20))
    merged = merged.dropna(subset=["interest", "receipts"])
    merged = merged[merged["receipts"] > 0]
    merged["interest_pct_receipts"] = merged["interest"] / merged["receipts"] * 100
    return merged[["date", "interest_pct_receipts"]].reset_index(drop=True)


def generate():
    df = compute_interest_burden()

    if df.empty:
        raise RuntimeError(
            "[26_federal_interest_burden] Aucune donnée récupérée depuis FRED "
            "(A091RC1Q027SBEA/FGRECPT). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    # Garde-fou de vraisemblance (même logique que le chart 16) : la charge
    # d'intérêts fédérale se situe entre ~5% et ~25% des recettes sur toute
    # l'histoire moderne. Hors de [0, 60], une série a changé d'unité ou de
    # définition -- échouer explicitement plutôt que publier un ratio absurde.
    last_value = df["interest_pct_receipts"].iloc[-1]
    if not (0 < last_value < 60):
        raise RuntimeError(
            f"[26_federal_interest_burden] Ratio calculé invraisemblable "
            f"({last_value:.1f}%, attendu entre 0 et 60%). Vérifier les unités de "
            "A091RC1Q027SBEA et FGRECPT sur fred.stlouisfed.org."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]
    ax.plot(df["date"], df["interest_pct_receipts"], color=COLOR_ACCENT, linewidth=2.0,
            label=format_last_value_label(
                "Intérêts fédéraux / recettes fédérales",
                f"{last_row['interest_pct_receipts']:.1f}%",
                series=df["interest_pct_receipts"], years_label=f"{DISPLAY_YEARS} ans"))
    mark_last_point(ax, last_row["date"], last_row["interest_pct_receipts"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Intérêts / recettes (%)", fontsize=9)
    ax.set_title("Charge d'intérêts fédérale en % des recettes de l'État US",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (A091RC1Q027SBEA, FGRECPT -- comptes nationaux BEA, SAAR) | "
        "Part des recettes fédérales absorbée par les intérêts de la dette avant toute autre dépense",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "26_federal_interest_burden.png")

    finalize_chart(fig, ax, out_path)

    print(f"[26_federal_interest_burden] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
