"""
Graphique : Nowcast GDPNow (Fed d'Atlanta) vs croissance du PIB réalisée

Séries FRED :
  - GDPNOW           : nowcast GDPNow de la Fed d'Atlanta, trimestriel, %
                       (croissance annualisée estimée du trimestre en cours ;
                       pour les trimestres passés, dernière estimation avant
                       la publication officielle)
  - A191RL1Q225SBEA  : croissance du PIB réel réalisée, trimestriel,
                       % annualisé (QoQ SAAR), données BEA

Pourquoi c'est utile : tous les autres graphiques du rapport sont
rétrospectifs -- ils décrivent ce qui s'est passé. GDPNow répond à la
question par laquelle une séance de comité commence : où en est la
croissance MAINTENANT ? Le modèle de la Fed d'Atlanta agrège chaque
publication macro (conso, capex, commerce extérieur...) en une estimation
du trimestre en cours, mise à jour plusieurs fois par mois, disponible un
trimestre avant le chiffre officiel du BEA. Le dernier point de la ligne
GDPNow est donc la seule donnée du rapport qui parle du présent. La
superposition avec le réalisé montre aussi la fiabilité historique du
nowcast (bonne en régime normal, prise en défaut dans les retournements
violents type 2020 -- c'est visible, et c'est une information en soi).

Sortie : PNG dans output/{periode}/28_gdpnow_vs_gdp.png
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
    finalize_chart, COLOR_ACCENT, COLOR_BENCHMARK
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS


def compute_gdpnow_vs_gdp(years: int = HISTORY_YEARS):
    """
    Retourne (nowcast, realized) : deux DataFrames triés par date.
    Pas de merge : les deux séries sont tracées indépendamment -- le
    nowcast a par construction un point de plus (le trimestre en cours,
    dont le réalisé n'existe pas encore), et c'est précisément ce point
    qui fait la valeur du chart. Un merge le ferait disparaître.
    """
    nowcast = get_series("GDPNOW", years=years)
    realized = get_series("A191RL1Q225SBEA", years=years)

    nowcast = nowcast.rename(columns={"value": "gdpnow"}).sort_values("date").reset_index(drop=True)
    realized = realized.rename(columns={"value": "gdp_growth"}).sort_values("date").reset_index(drop=True)
    return nowcast, realized


def generate():
    nowcast, realized = compute_gdpnow_vs_gdp()

    if nowcast.empty or realized.empty:
        raise RuntimeError(
            "[28_gdpnow_vs_gdp] Aucune donnée récupérée depuis FRED "
            "(GDPNOW/A191RL1Q225SBEA). Vérifie FRED_API_KEY et la connectivité réseau."
        )

    fig, ax = setup_figure()
    date_min = min(nowcast["date"].min(), realized["date"].min())
    last_date = max(nowcast["date"].max(), realized["date"].max())
    add_recession_bands(ax, date_min=date_min, date_max=last_date)

    last_realized = realized.iloc[-1]
    last_nowcast = nowcast.iloc[-1]

    # Réalisé en barres grises (le fait accompli), nowcast en ligne bleue
    # (l'estimation vivante). Largeur de barre en jours, adaptée au pas
    # trimestriel -- même approche que le chart 09.
    bars = ax.bar(realized["date"], realized["gdp_growth"], width=70,
                  color=COLOR_BENCHMARK, alpha=0.55, zorder=2,
                  label=format_last_value_label("PIB réalisé (QoQ annualisé, BEA)",
                                                f"{last_realized['gdp_growth']:+.1f}%"))
    line_nowcast, = ax.plot(nowcast["date"], nowcast["gdpnow"], color=COLOR_ACCENT,
                            linewidth=2.0, marker="o", markersize=4, zorder=3,
                            label=format_last_value_label(
                                "Nowcast GDPNow (trimestre en cours inclus)",
                                f"{last_nowcast['gdpnow']:+.1f}%"))
    ax.axhline(0, color="#555555", linewidth=0.9, linestyle="--", zorder=1)
    mark_last_point(ax, last_nowcast["date"], last_nowcast["gdpnow"])

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Croissance du PIB réel, annualisée (%)", fontsize=9)
    ax.set_title("Croissance US en temps réel : nowcast GDPNow vs PIB réalisé",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)

    add_source_footer(
        fig,
        "Source: FRED (GDPNOW -- Fed d'Atlanta, A191RL1Q225SBEA -- BEA) | Le dernier point "
        "GDPNow estime le trimestre en cours, ~1 trimestre avant le chiffre officiel",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "28_gdpnow_vs_gdp.png")

    finalize_chart(fig, ax, out_path, handles=[bars, line_nowcast])

    print(f"[28_gdpnow_vs_gdp] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
