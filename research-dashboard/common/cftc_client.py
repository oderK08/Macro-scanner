"""
Wrapper autour de l'API publique CFTC (Commitments of Traders) avec cache
local incrémental.

Source : Public Reporting Environment de la CFTC (publicreporting.cftc.gov),
une API Socrata officielle et gratuite. Pas de clé requise -- la CFTC ne
distribue pas de tokens pour cette API et documente qu'un usage modéré sans
token est attendu. Un rate limiting de courtoisie est appliqué ici.

Dataset utilisé : "Legacy - Futures Only" (identifiant Socrata 6dca-aqww),
le rapport COT historique -- positions des "non-commercials" (spéculateurs :
hedge funds, CTA...) vs "commercials" (hedgers industriels), hebdomadaire
(arrêté le mardi, publié le vendredi), historique remontant à 1986.

Identification des contrats : par cftc_contract_market_code, PAS par nom.
Les noms de contrats ("E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE"...)
sont réécrits par la CFTC au fil des ans ; les codes numériques sont
stables sur des décennies -- critère indispensable pour un projet qui doit
tourner sans maintenance.

Métrique calculée : position nette des non-commercials en % de l'open
interest total :
    net_pct_oi = (longs_non_comm - shorts_non_comm) / open_interest * 100
La normalisation par l'open interest rend les contrats comparables entre
eux et dans le temps (l'OI de l'e-mini S&P a été multiplié par plusieurs
fois en 20 ans -- une position nette en nombre de contrats n'est pas
comparable d'une époque à l'autre).
"""
import time
import requests
import pandas as pd

from common.cache_utils import merge_incremental, load_cache, get_last_cached_date

COT_LEGACY_FUTURES_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
SLEEP_BETWEEN_CALLS = 1.0  # courtoisie : API sans token, usage très modéré
REQUEST_TIMEOUT = 60

# User-Agent identifiable, même politesse qu'avec la SEC et Wikipedia.
HEADERS = {"User-Agent": "research-dashboard (usage personnel non-commercial)"}


def get_cot_net_positioning(contract_code: str, years: int = 10) -> pd.DataFrame:
    """
    Récupère la position nette des non-commercials en % de l'open interest
    pour un contrat donné, avec cache incrémental.

    Args:
        contract_code: code CFTC du marché, ex "13874A" (E-mini S&P 500).
            Toujours le code, jamais le nom (voir docstring du module).
        years: fenêtre d'historique en années.

    Returns:
        DataFrame avec colonnes 'date' et 'value' (net % OI), trié par date.
    """
    cache_key = f"cftc_cot_{contract_code}"
    date_debut = pd.Timestamp.today() - pd.DateOffset(years=years)

    last_cached = get_last_cached_date(cache_key)
    fetch_from = last_cached + pd.Timedelta(days=1) if last_cached is not None else date_debut

    params = {
        "$select": ("report_date_as_yyyy_mm_dd,"
                    "noncomm_positions_long_all,noncomm_positions_short_all,"
                    "open_interest_all"),
        "$where": (f"cftc_contract_market_code='{contract_code}' AND "
                   f"report_date_as_yyyy_mm_dd>='{fetch_from.strftime('%Y-%m-%d')}T00:00:00.000'"),
        "$order": "report_date_as_yyyy_mm_dd",
        # Hebdomadaire : ~52 lignes/an/contrat. 50 000 couvre très largement
        # toute fenêtre raisonnable sans avoir besoin de pagination.
        "$limit": 50000,
    }

    resp = requests.get(COT_LEGACY_FUTURES_URL, params=params, headers=HEADERS,
                        timeout=REQUEST_TIMEOUT)
    time.sleep(SLEEP_BETWEEN_CALLS)
    resp.raise_for_status()
    rows = resp.json()

    if rows:
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
        for col in ["noncomm_positions_long_all", "noncomm_positions_short_all", "open_interest_all"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["noncomm_positions_long_all", "noncomm_positions_short_all",
                               "open_interest_all"])
        df = df[df["open_interest_all"] > 0]
        df["value"] = ((df["noncomm_positions_long_all"] - df["noncomm_positions_short_all"])
                       / df["open_interest_all"] * 100)
        merge_incremental(cache_key, df[["date", "value"]])

    full_df = load_cache(cache_key)
    full_df = full_df[full_df["date"] >= date_debut]
    return full_df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
