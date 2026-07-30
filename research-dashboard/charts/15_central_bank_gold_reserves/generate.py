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
DISPLAY_YEARS = 7
TOP_N_BUYERS = 6

# Pool de pays CANDIDATS pour le classement des "plus gros acheteurs sur 7
# ans" -- pas une liste finale, juste les candidats plausibles parmi
# lesquels on calcule qui a le plus acheté en tonnes. Liste ajustable
# librement : plus il y a de candidats, plus le classement est robuste.
BUYER_CANDIDATES = [
    "China", "Russia", "India", "Turkey", "Poland", "Kazakhstan",
    "Czech Republic", "Singapore", "Qatar", "Uzbekistan", "Egypt", "Iraq",
]

# Pays de référence : affichés comme un simple point/repère à droite du
# graphique (avec leur valeur en texte), PAS comme une ligne complète --
# leurs réserves sont énormes et quasi figées depuis des décennies, une
# ligne plate écraserait l'échelle et rendrait les vrais acheteurs actifs
# illisibles.
REFERENCE_COUNTRIES = ["United States"]

TONNES_PER_MILLION_TROY_OZ = 31.1034768  # 1 once troy = 31.1034768 grammes

BUYER_COLORS = ["#c0392b", "#1a3a5c", "#e08e79", "#2f6690", "#9b59b6", "#5b8ab8", "#8fb8d8", "#7f2020"]


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
    """
    Retourne un DataFrame long: date, country, gold_tonnes.
    Récupère TOUS les pays donnés (candidats acheteurs + références) --
    le tri "qui a le plus acheté" se fait ensuite dans generate(), pas ici,
    pour que cette fonction reste réutilisable indépendamment du classement.
    """
    if countries is None:
        countries = BUYER_CANDIDATES + REFERENCE_COUNTRIES

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


def _rank_top_buyers(df: pd.DataFrame, candidates: list, top_n: int) -> list:
    """
    Classe les pays candidats par tonnes achetées sur la fenêtre affichée
    (dernière valeur - première valeur), et retourne les top_n noms de pays.
    Un pays qui a VENDU de l'or (variation négative) ne sera jamais mieux
    classé qu'un pays qui en a acheté, quel que soit son niveau absolu.
    """
    changes = []
    for country in candidates:
        sub = df[df["country"] == country].sort_values("date")
        if len(sub) < 2:
            continue
        change = sub["gold_tonnes"].iloc[-1] - sub["gold_tonnes"].iloc[0]
        changes.append((country, change))

    changes.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in changes[:top_n]]


def generate():
    df = compute_gold_reserves_by_country()

    if df.empty:
        raise RuntimeError(
            "[15_central_bank_gold_reserves] Aucune donnée récupérée depuis DBnomics pour aucun pays. "
            "Vérifie la connectivité réseau vers api.db.nomics.world, et si le problème persiste, "
            "la structure de requête a probablement besoin d'un ajustement (voir avertissement en tête "
            "de ce fichier)."
        )

    top_buyers = _rank_top_buyers(df, BUYER_CANDIDATES, TOP_N_BUYERS)
    if not top_buyers:
        raise RuntimeError(
            "[15_central_bank_gold_reserves] Aucun pays candidat n'a pu être classé "
            "(pas assez de données récupérées pour calculer une variation)."
        )

    fig, ax = setup_figure()
    last_date = df["date"].max()

    for i, country in enumerate(top_buyers):
        sub = df[df["country"] == country].sort_values("date")
        if sub.empty:
            continue
        color = BUYER_COLORS[i % len(BUYER_COLORS)]
        ax.plot(sub["date"], sub["gold_tonnes"], color=color,
                linewidth=1.8, marker="o", markersize=2.5, label=country)

    format_date_axis(ax, tight_to_last_point=last_date)
    ax.set_ylabel("Réserves d'or (tonnes)", fontsize=9)
    ax.set_title(f"Top {TOP_N_BUYERS} des banques centrales ayant le plus acheté d'or sur {DISPLAY_YEARS} ans",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_date)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    # Pays de référence (États-Unis) : un simple repère textuel hors échelle,
    # pas une ligne complète -- leurs réserves (~8 133 tonnes, quasi figées
    # depuis les années 1970) écraseraient sinon toute l'échelle et
    # rendraient les acheteurs actifs illisibles.
    for ref_country in REFERENCE_COUNTRIES:
        sub = df[df["country"] == ref_country].sort_values("date")
        if sub.empty:
            continue
        last_value = sub["gold_tonnes"].iloc[-1]
        ax.annotate(
            f"Repère : {ref_country}\n≈ {last_value:,.0f} t (hors échelle)".replace(",", " "),
            xy=(1.0, 0.97), xycoords="axes fraction",
            ha="right", va="top", fontsize=8, color="#888888", style="italic",
        )

    add_source_footer(
        fig,
        "Source: DBnomics (IMF/IFS) | Classement par variation des réserves sur la période affichée, "
        "pas par niveau absolu | Volume converti d'onces troy en tonnes (1 once troy = 31.1035g)",
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
