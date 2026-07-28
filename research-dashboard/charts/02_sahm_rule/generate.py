"""
Graphique : Sahm Rule Recession Indicator

Calcul : moyenne mobile 3 mois du taux de chômage (UNRATE) moins son plus
bas sur les 12 derniers mois. Un seuil de 0.5 point a historiquement
annoncé le début de chaque récession US depuis 1970, en temps quasi réel
— contrairement à "le chômage augmente", qui est un signal bruité et tardif.

FRED fournit déjà la série calculée officiellement (SAHMREALTIME), mais on
la recalcule nous-mêmes à partir de UNRATE pour comprendre/contrôler le calcul
et ne dépendre que d'une seule série brute.

Sortie : PNG dans output/{periode}/02_sahm_rule.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

SAHM_THRESHOLD = 0.5


def compute_sahm_rule(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, unrate, sahm_indicator.
    On télécharge 1.5 an de plus que la fenêtre affichée pour pouvoir
    calculer correctement la moyenne mobile 3M et le minimum 12M dès le
    premier point affiché.
    """
    unrate = get_series("UNRATE", years=years + 2)
    unrate = unrate.sort_values("date").reset_index(drop=True)
    unrate = unrate.rename(columns={"value": "unrate"})

    unrate["ma3"] = unrate["unrate"].rolling(window=3).mean()
    unrate["min12_of_ma3"] = unrate["ma3"].rolling(window=12).min()
    unrate["sahm_indicator"] = unrate["ma3"] - unrate["min12_of_ma3"]

    unrate = unrate.dropna(subset=["sahm_indicator"])
    date_min = unrate["date"].max() - pd.DateOffset(years=years)
    return unrate[unrate["date"] >= date_min].reset_index(drop=True)


def generate():
    df = compute_sahm_rule()

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    ax.plot(df["date"], df["sahm_indicator"], color=COLOR_ACCENT, linewidth=2.0,
            label="Indicateur Sahm")
    ax.axhline(SAHM_THRESHOLD, color="#c0392b", linewidth=1.2, linestyle="--",
               label=f"Seuil de déclenchement ({SAHM_THRESHOLD})")
    ax.axhline(0, color="#999999", linewidth=0.8)

    format_date_axis(ax)
    ax.set_ylabel("Points de %", fontsize=9)
    ax.set_title("Sahm Rule Recession Indicator",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    last_row = df.iloc[-1]
    status = "SEUIL FRANCHI" if last_row["sahm_indicator"] >= SAHM_THRESHOLD else "sous le seuil"
    ax.annotate(
        f"Dernière valeur: {last_row['sahm_indicator']:.2f} ({status})",
        xy=(last_row["date"], last_row["sahm_indicator"]),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8.5,
        color=COLOR_ACCENT,
        fontweight="bold",
    )

    add_source_footer(fig, "Source: FRED (UNRATE) | Calcul: MM3(chômage) - min12M(MM3)")

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "02_sahm_rule.png")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[02_sahm_rule] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
