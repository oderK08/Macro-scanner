"""
Graphique : Réserves d'or des banques centrales, par pays

Source : DBnomics (https://db.nomics.world), qui republie les statistiques
du FMI (base IMF/IFS -- International Financial Statistics) en JSON simple.

⚠️ AVERTISSEMENT IMPORTANT : cette source est différente de FRED/EDGAR
utilisées ailleurs dans ce projet. Le domaine api.db.nomics.world n'a pas
pu être testé en conditions réelles au moment de l'écriture de ce script
(inaccessible depuis l'environnement de développement). La logique de
recherche/extraction est construite sur la documentation officielle et des
exemples confirmés, mais un premier run réel peut révéler un ajustement
nécessaire -- si ce graphique échoue, regarde le message d'erreur (il inclut
un extrait de la réponse brute de l'API pour faciliter le diagnostic).

Méthode : pour chaque pays suivi, on interroge l'API de RECHERCHE de
DBnomics en texte libre (pas d'identifiant pays codé en dur -- le FMI
utilise ses propres codes non-standards, ex: "1C_459" pour un pays donné,
pas un code ISO), on prend la série mensuelle de réserves d'or (volume en
onces troy) la plus pertinente, puis on convertit en tonnes.

Pourquoi c'est utile : le narratif de "dé-dollarisation" (les banques
centrales, notamment émergentes, qui diversifient leurs réserves hors USD
en accumulant de l'or) est un des grands sujets macro depuis 2022 (gel des
réserves russes). Ce graphique permet de suivre concrètement qui achète,
à quel rythme, et si la tendance s'essouffle ou s'accélère.

Sortie : PNG dans output/{periode}/15_central_bank_gold_reserves.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.dbnomics_client import search_series, get_series_observations
from common.chart_style import setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle
from common.config import get_current_period_label, OUTPUT_DIR

PROVIDER = "IMF"
DATASET = "IFS"
DISPLAY_YEARS = 8

# Pays suivis : parmi les plus gros acheteurs d'or connus depuis 2022
# (narratif de dé-dollarisation). Liste ajustable librement.
COUNTRIES = ["China", "Russia", "India", "Turkey", "Poland", "Kazakhstan", "Czech Republic"]

TONNES_PER_MILLION_TROY_OZ = 31.1034768  # 1 once troy = 31.1034768 grammes

COUNTRY_COLORS = {
    "China": "#c0392b",
    "Russia": "#1a3a5c",
    "India": "#e08e79",
    "Turkey": "#2f6690",
    "Poland": "#8fb8d8",
    "Kazakhstan": "#5b8ab8",
    "Czech Republic": "#9b59b6",
}


def _find_best_series(country: str):
    """
    Cherche la série mensuelle de réserves d'or (volume) la plus pertinente
    pour un pays donné, via recherche texte libre (pas d'identifiant codé
    en dur). Retourne le series_code, ou None si rien de convaincant trouvé.
    """
    query = f"{country} gold official reserve assets volume troy ounces"
    docs = search_series(PROVIDER, DATASET, query, limit=20)

    for doc in docs:
        series_code = doc.get("series_code", "")
        series_name = doc.get("series_name", "")
        is_monthly = series_code.startswith("M.")
        mentions_gold = "gold" in series_name.lower()
        mentions_volume = "volume" in series_name.lower() or "ozt" in series_code.lower()
        mentions_country = country.lower() in series_name.lower()

        if is_monthly and mentions_gold and mentions_volume and mentions_country:
            return series_code, series_name

    return None, None


def compute_gold_reserves_by_country(years: int = DISPLAY_YEARS, countries: list = None) -> pd.DataFrame:
    """Retourne un DataFrame long: date, country, gold_tonnes."""
    if countries is None:
        countries = COUNTRIES

    records = []
    for country in countries:
        try:
            series_code, series_name = _find_best_series(country)
            if series_code is None:
                print(f"  [avertissement] {country}: aucune série pertinente trouvée -- ignoré")
                continue

            obs = get_series_observations(PROVIDER, DATASET, series_code)
            obs["gold_tonnes"] = obs["value"] * TONNES_PER_MILLION_TROY_OZ

            date_min = obs["date"].max() - pd.DateOffset(years=years)
            obs = obs[obs["date"] >= date_min]

            for _, row in obs.iterrows():
                records.append({"date": row["date"], "country": country, "gold_tonnes": row["gold_tonnes"]})

            print(f"[15_central_bank_gold_reserves] {country}: {len(obs)} points récupérés ({series_code})")
        except Exception as e:
            print(f"  [avertissement] {country}: échec de récupération ({e}) -- ignoré, on continue")
            continue

    return pd.DataFrame(records)


def generate():
    df = compute_gold_reserves_by_country()

    if df.empty:
        raise RuntimeError(
            "[15_central_bank_gold_reserves] Aucune donnée récupérée depuis DBnomics pour aucun pays. "
            "Vérifie la connectivité réseau vers api.db.nomics.world, et si le problème persiste, "
            "la structure de requête a probablement besoin d'un ajustement (voir avertissement en tête "
            "de ce fichier)."
        )

    fig, ax = setup_figure()
    last_date = df["date"].max()

    for country in COUNTRIES:
        sub = df[df["country"] == country].sort_values("date")
        if sub.empty:
            continue
        ax.plot(sub["date"], sub["gold_tonnes"], color=COUNTRY_COLORS.get(country, "#888888"),
                linewidth=1.8, marker="o", markersize=2.5, label=country)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Réserves d'or (tonnes)", fontsize=9)
    ax.set_title("Réserves d'or des banques centrales, par pays",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=2)

    add_source_footer(
        fig,
        "Source: DBnomics (IMF/IFS) | Volume converti d'onces troy en tonnes (1 once troy = 31.1035g)",
        as_of_date=last_date,
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "15_central_bank_gold_reserves.png")

    fig.tight_layout(rect=[0, 0.05, 0.97, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[15_central_bank_gold_reserves] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
