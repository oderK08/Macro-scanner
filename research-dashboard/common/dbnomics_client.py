"""
Client pour l'API DBnomics (https://db.nomics.world), qui republie en JSON
simple les données statistiques du FMI (entre autres), dont les réserves
d'or des banques centrales (base IMF/IFS).

Pourquoi DBnomics plutôt que l'API du FMI en direct : l'API du FMI utilise
le format SDMX, plus lourd et plus technique, avec une construction de
requête en plusieurs étapes et des identifiants pays propres au FMI (pas de
simple code ISO). DBnomics republie les mêmes données en JSON via une API
REST beaucoup plus simple, sans clé API.

⚠️ Ce client n'a pas pu être testé en conditions réelles (le domaine
api.db.nomics.world n'était pas accessible depuis l'environnement de
développement). La structure de requête est basée sur la documentation
officielle DBnomics et des exemples confirmés, mais un premier run réel
peut révéler un ajustement nécessaire (comme ça a déjà été le cas pour
d'autres sources dans ce projet, ex: ACMTP10 -> THREEFYTP10).

Approche volontairement robuste : plutôt que de coder en dur des
identifiants pays FMI (qui ne suivent PAS le format ISO standard, ex:
"1C_459" pour un pays), on interroge l'API de RECHERCHE de DBnomics avec le
nom du pays en texte libre, et on prend le meilleur résultat -- ça évite
d'avoir une liste fragile d'identifiants à maintenir/deviner.
"""
import requests
import pandas as pd

BASE_URL = "https://api.db.nomics.world/v22"
TIMEOUT = 30


def search_series(provider: str, dataset: str, query: str, limit: int = 20) -> list:
    """
    Recherche des séries par texte libre dans un dataset DBnomics donné.
    Retourne une liste de dicts avec au moins 'series_code' et 'series_name'.

    Lève une exception explicite en cas d'échec réseau ou de structure de
    réponse inattendue -- à charge de l'appelant de décider s'il continue
    sans ce pays ou s'il arrête tout (voir generate.py du chart concerné).
    """
    url = f"{BASE_URL}/series/{provider}/{dataset}"
    params = {"q": query, "format": "json", "limit": limit, "observations": 0}

    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    try:
        docs = data["series"]["docs"]
    except (KeyError, TypeError) as e:
        raise RuntimeError(
            f"Structure de réponse DBnomics inattendue pour la recherche '{query}' : "
            f"clés trouvées {list(data.keys())}. Réponse brute (tronquée): {str(data)[:500]}"
        ) from e

    return docs


def get_series_observations(provider: str, dataset: str, series_code: str) -> pd.DataFrame:
    """
    Récupère les observations (date, valeur) d'une série DBnomics précise.
    Retourne un DataFrame avec colonnes: date, value.
    """
    url = f"{BASE_URL}/series/{provider}/{dataset}/{series_code}"
    params = {"observations": 1, "format": "json"}

    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    try:
        doc = data["series"]["docs"][0]
        periods = doc["period"]
        values = doc["value"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"Structure de réponse DBnomics inattendue pour la série '{series_code}' : "
            f"clés trouvées {list(data.keys())}. Réponse brute (tronquée): {str(data)[:500]}"
        ) from e

    df = pd.DataFrame({"date": pd.to_datetime(periods), "value": values})
    return df.dropna(subset=["value"]).reset_index(drop=True)
