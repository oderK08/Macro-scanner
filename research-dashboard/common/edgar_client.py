"""
Wrapper autour de l'API SEC EDGAR (data.sec.gov) avec rate limiting et cache.

Points importants (obligatoires côté SEC) :
- User-Agent identifiable requis sur CHAQUE requête (nom + email), sinon
  risque de blocage même à faible débit.
- Limite stricte : 10 requêtes/seconde par IP, tous endpoints confondus.
  On se cale ici sur ~5/s par sécurité (voir SLEEP_BETWEEN_CALLS).

Endpoints utilisés :
- companyfacts   : toutes les données XBRL d'une entreprise (par CIK)
- frames         : un concept XBRL donné, pour TOUTES les entreprises,
                    sur une période donnée en un seul appel (le plus efficace
                    pour de l'agrégation sectorielle/indicielle)
- company_tickers.json : mapping ticker -> CIK
"""
import time
import json
import requests
import pandas as pd
from common.config import EDGAR_USER_AGENT
from common.cache_utils import merge_incremental, load_cache

BASE_URL = "https://data.sec.gov"
SLEEP_BETWEEN_CALLS = 0.2  # ~5 requêtes/seconde, sous la limite de 10/s

_ticker_to_cik_cache = None


def _headers():
    if not EDGAR_USER_AGENT:
        raise RuntimeError(
            "EDGAR_USER_AGENT n'est pas définie. "
            "La SEC exige un User-Agent identifiable, ex: "
            "export EDGAR_USER_AGENT='Jean Dupont jean.dupont@email.com'"
        )
    return {"User-Agent": EDGAR_USER_AGENT}


def get_ticker_to_cik_map() -> dict:
    """
    Récupère le mapping ticker -> CIK (10 chiffres, zero-paddé).
    Mis en cache en mémoire pour la durée du run (fichier stable, change peu).
    """
    global _ticker_to_cik_cache
    if _ticker_to_cik_cache is not None:
        return _ticker_to_cik_cache

    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    data = resp.json()

    mapping = {}
    for entry in data.values():
        ticker = entry["ticker"].upper()
        cik = str(entry["cik_str"]).zfill(10)
        mapping[ticker] = cik

    _ticker_to_cik_cache = mapping
    time.sleep(SLEEP_BETWEEN_CALLS)
    return mapping


def get_company_facts(ticker: str) -> dict:
    """
    Récupère toutes les données XBRL (companyfacts) pour un ticker donné.
    Retourne le JSON brut de la SEC.
    """
    ticker_map = get_ticker_to_cik_map()
    cik = ticker_map.get(ticker.upper())
    if cik is None:
        raise ValueError(f"Ticker '{ticker}' introuvable dans le mapping SEC.")

    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
    resp = requests.get(url, headers=_headers())
    time.sleep(SLEEP_BETWEEN_CALLS)

    if resp.status_code == 404:
        raise ValueError(f"Pas de données XBRL pour {ticker} (CIK {cik}).")
    resp.raise_for_status()
    return resp.json()


def extract_concept_series(facts_json: dict, concepts: list, unit: str = "USD") -> pd.DataFrame:
    """
    Extrait une série temporelle pour le premier concept XBRL trouvé parmi
    une liste de candidats (fallback), typiquement pour gérer les différences
    de tagging entre entreprises (ex: capex tagué différemment selon les boîtes).

    Args:
        facts_json: JSON retourné par get_company_facts()
        concepts: liste ordonnée de concepts XBRL à essayer (ex: CAPEX_XBRL_CONCEPTS)
        unit: unité recherchée (par défaut USD)

    Returns:
        DataFrame avec colonnes: end_date, value, fiscal_period, fiscal_year, form
    """
    us_gaap = facts_json.get("facts", {}).get("us-gaap", {})

    for concept in concepts:
        if concept in us_gaap:
            units = us_gaap[concept].get("units", {})
            if unit in units:
                rows = units[unit]
                df = pd.DataFrame(rows)
                # On garde seulement les 10-Q et 10-K pour éviter les doublons
                # d'amendements (10-Q/A, etc.)
                df = df[df["form"].isin(["10-Q", "10-K"])]
                df = df.rename(columns={"end": "end_date", "fp": "fiscal_period", "fy": "fiscal_year"})
                return df[["end_date", "value", "fiscal_period", "fiscal_year", "form"]].sort_values("end_date")

    return pd.DataFrame(columns=["end_date", "value", "fiscal_period", "fiscal_year", "form"])


def get_frame(concept: str, period: str, unit: str = "USD") -> pd.DataFrame:
    """
    Récupère un concept XBRL donné pour TOUTES les entreprises sur une période
    donnée en un seul appel (endpoint 'frames'). Très efficace pour de
    l'agrégation large (ex: capex S&P 500) plutôt que d'interroger CIK par CIK.

    Args:
        concept: concept XBRL, ex "PaymentsToAcquirePropertyPlantAndEquipment"
        period: format SEC, ex "CY2025Q2I" (instantané) ou "CY2025Q2" (cumulatif période)
        unit: unité (défaut USD)

    Returns:
        DataFrame avec colonnes: cik, entity_name, value
    """
    url = f"{BASE_URL}/api/xbrl/frames/us-gaap/{concept}/{unit}/{period}.json"
    resp = requests.get(url, headers=_headers())
    time.sleep(SLEEP_BETWEEN_CALLS)

    if resp.status_code == 404:
        return pd.DataFrame(columns=["cik", "entity_name", "value"])
    resp.raise_for_status()

    data = resp.json().get("data", [])
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["cik", "entity_name", "value"])

    df = df.rename(columns={"cik": "cik", "entityName": "entity_name", "val": "value"})
    return df[["cik", "entity_name", "value"]]
