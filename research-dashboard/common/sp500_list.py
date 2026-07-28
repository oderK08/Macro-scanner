"""
Récupération de la composition réelle et à jour de l'indice S&P 500.

Contrairement à un échantillon statique maintenu à la main, ce module va
chercher la VRAIE liste des ~500 constituants actuels, avec leur secteur
GICS officiel et leur CIK, directement depuis la page Wikipedia dédiée --
qui est mise à jour par la communauté à chaque changement de composition de
l'indice.

Pourquoi Wikipedia plutôt que EDGAR : il n'existe aucune API SEC listant
"les constituants actuels du S&P 500" (l'indice est une propriété de S&P
Dow Jones Indices, pas une entité réglementaire). Wikipedia est la source
gratuite la plus fiable et la mieux maintenue pour cette information
précise.

Robustesse : le résultat est mis en cache localement (data_cache/). Si la
page Wikipedia est temporairement inaccessible ou que sa structure change
de façon incompatible, on retombe sur ce cache local plutôt que de faire
planter tous les graphiques qui en dépendent.
"""
import os
import io
import requests
import pandas as pd

from common.config import DATA_CACHE_DIR

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
CACHE_PATH = os.path.join(DATA_CACHE_DIR, "sp500_constituents.csv")

# Wikipedia demande un User-Agent identifiable pour les requêtes automatisées
# (comme la SEC) -- ne pas l'omettre sous peine de blocage.
HEADERS = {"User-Agent": "research-dashboard (usage personnel non-commercial)"}

_cached_df = None  # cache mémoire pour la durée du run, évite de re-fetch plusieurs fois


def _fetch_from_wikipedia() -> pd.DataFrame:
    """
    Récupère et parse la table des constituants depuis Wikipedia.
    Lève une exception si la page est inaccessible ou si sa structure a
    changé de façon incompatible (colonnes attendues absentes).
    """
    resp = requests.get(WIKIPEDIA_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    tables = pd.read_html(io.StringIO(resp.text))
    df = tables[0]  # la première table de la page est la liste des constituants

    expected_cols = {"Symbol", "GICS Sector", "GICS Sub-Industry", "CIK"}
    if not expected_cols.issubset(set(df.columns)):
        raise ValueError(
            f"Structure Wikipedia inattendue : colonnes trouvées {list(df.columns)}, "
            f"attendues au moins {expected_cols}"
        )

    df = df.rename(columns={
        "Symbol": "ticker",
        "Security": "name",
        "GICS Sector": "sector",
        "GICS Sub-Industry": "sub_industry",
        "CIK": "cik",
    })
    df["cik"] = df["cik"].astype(str).str.zfill(10)
    df["ticker"] = df["ticker"].astype(str).str.strip()

    return df[["ticker", "name", "sector", "sub_industry", "cik"]]


def get_sp500_constituents(force_refresh: bool = False) -> pd.DataFrame:
    """
    Retourne un DataFrame avec colonnes: ticker, name, sector, sub_industry, cik.
    Environ 500-505 lignes (quelques entreprises ont 2 classes d'actions,
    donc 2 tickers pour le même CIK -- géré naturellement par les charts qui
    dédupliquent par CIK via un set()).

    Ordre de résolution :
    1. Cache mémoire (si déjà chargé pendant ce run et force_refresh=False)
    2. Wikipedia en direct (source de vérité, mise à jour communautaire)
    3. Cache disque local (repli si Wikipedia est inaccessible)

    Si aucune des trois sources ne fonctionne, lève une exception claire
    plutôt que de renvoyer une liste vide silencieusement.
    """
    global _cached_df
    if _cached_df is not None and not force_refresh:
        return _cached_df

    try:
        df = _fetch_from_wikipedia()
        os.makedirs(DATA_CACHE_DIR, exist_ok=True)
        df.to_csv(CACHE_PATH, index=False)
        print(f"[sp500_list] Liste S&P 500 récupérée depuis Wikipedia ({len(df)} lignes) et mise en cache.")
        _cached_df = df
        return df
    except Exception as e:
        print(f"[sp500_list] AVERTISSEMENT: échec de récupération depuis Wikipedia ({e}).")
        if os.path.exists(CACHE_PATH):
            print(f"[sp500_list] Repli sur le cache local: {CACHE_PATH}")
            df = pd.read_csv(CACHE_PATH, dtype={"cik": str})
            df["cik"] = df["cik"].str.zfill(10)
            _cached_df = df
            return df
        raise RuntimeError(
            "[sp500_list] Impossible de récupérer la composition du S&P 500 : "
            "échec Wikipedia ET aucun cache local disponible. "
            "Vérifie la connectivité réseau ou la structure de la page Wikipedia."
        ) from e
