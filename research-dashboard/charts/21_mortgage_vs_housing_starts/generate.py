"""
Graphique : Taux hypothécaire 30 ans vs mises en chantier de logements

Séries FRED :
  - MORTGAGE30US : taux hypothécaire fixe 30 ans (enquête Freddie Mac),
                   hebdomadaire, %
  - HOUST        : mises en chantier de logements (Census Bureau), mensuel,
                   en MILLIERS d'unités, rythme annualisé désaisonnalisé (SAAR)

Choix de HOUST plutôt que les ventes de logements existants (NAR) : les
mises en chantier sont une statistique OFFICIELLE du Census Bureau,
publiée sans interruption depuis 1959 -- une série privée (NAR) peut
changer de méthodologie ou disparaître de FRED (c'est déjà arrivé à des
séries privées). Critère de robustesse pour un projet sans maintenance.

Pourquoi c'est utile : l'immobilier résidentiel est LE canal de
transmission de la politique monétaire à l'économie réelle -- premier
secteur à casser quand les taux montent, premier à repartir quand ils
baissent ("housing is the business cycle", Leamer 2007). Les mises en
chantier sont en plus un moteur direct d'emploi (construction) et de
demande (matériaux, équipement). La paire taux hypothécaire / mises en
chantier montre la transmission en action, avec son délai.

Sortie : PNG dans output/{periode}/21_mortgage_vs_housing_starts.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

COLOR_STARTS = "#2e7d52"


def compute_mortgage_vs_starts(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: date, mortgage_rate, housing_starts.
    MORTGAGE30US est hebdomadaire, HOUST mensuel -> merge_asof sur la grille
    hebdomadaire du taux, tolérance 45 jours pour raccrocher le dernier
    point mensuel connu des mises en chantier.
    """
    mortgage = get_series("MORTGAGE30US", years=years)
    starts = get_series("HOUST", years=years)

    mortgage = mortgage.rename(columns={"value": "mortgage_rate"}).sort_values("date")
    starts = starts.rename(columns={"value": "housing_starts"}).sort_values("date")

    merged = pd.merge_asof(mortgage, starts, on="date", direction="backward",
                           tolerance=pd.Timedelta(days=45))
    return merged.dropna(subset=["mortgage_rate"]).reset_index(drop=True)


def generate():
    df = compute_mortgage_vs_starts()

    if df.empty:
        raise RuntimeError(
            "[21_mortgage_vs_housing_starts] Aucune donnée récupérée depuis FRED "
            "(MORTGAGE30US/HOUST). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    ax2 = ax.twinx()
    ax2.patch.set_visible(False)  # laisse bandes de récession et grille de ax visibles

    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    line_rate, = ax.plot(df["date"], df["mortgage_rate"], color=COLOR_ACCENT, linewidth=1.7,
                         label="Taux hypothécaire 30 ans (%, éch. gauche)", zorder=3)

    starts_available = df.dropna(subset=["housing_starts"])
    line_starts, = ax2.plot(starts_available["date"], starts_available["housing_starts"],
                            color=COLOR_STARTS, linewidth=1.4,
                            label="Mises en chantier (milliers, SAAR, éch. droite)", zorder=2)

    last_row = df.iloc[-1]
    last_starts_row = starts_available.iloc[-1] if not starts_available.empty else None

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Taux hypothécaire 30 ans (%)", fontsize=9, color=COLOR_ACCENT)
    ax2.set_ylabel("Mises en chantier (milliers, SAAR)", fontsize=9, color=COLOR_STARTS)
    ax2.tick_params(colors=COLOR_STARTS, labelsize=9)
    ax2.spines["top"].set_visible(False)

    ax.set_title("Taux hypothécaire 30 ans vs mises en chantier de logements",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    handles = [line_rate, line_starts]
    ax.legend(handles, [h.get_label() for h in handles], loc="upper left",
              fontsize=8.5, frameon=False)

    ax.plot(last_row["date"], last_row["mortgage_rate"], marker="o", markersize=5,
            color=COLOR_ACCENT, zorder=5)
    ax.annotate(
        f"{last_row['mortgage_rate']:.2f}%",
        xy=(last_row["date"], last_row["mortgage_rate"]),
        xytext=(10, 0), textcoords="offset points",
        fontsize=8.5, color=COLOR_ACCENT, fontweight="bold", va="center",
    )
    if last_starts_row is not None:
        ax2.plot(last_starts_row["date"], last_starts_row["housing_starts"], marker="o",
                 markersize=5, color=COLOR_STARTS, zorder=5)
        ax2.annotate(
            f"{last_starts_row['housing_starts']:.0f}k",
            xy=(last_starts_row["date"], last_starts_row["housing_starts"]),
            xytext=(10, 0), textcoords="offset points",
            fontsize=8.5, color=COLOR_STARTS, fontweight="bold", va="center",
        )

    add_source_footer(
        fig,
        "Source: FRED (MORTGAGE30US -- enquête Freddie Mac, HOUST -- Census Bureau) | "
        "Relation inverse attendue : taux en hausse -> chantiers en baisse, avec délai",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "21_mortgage_vs_housing_starts.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[21_mortgage_vs_housing_starts] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
