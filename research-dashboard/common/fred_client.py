"""
Wrapper autour de fredapi avec cache local incrémental.

Installation requise : pip install fredapi

Limite FRED avec clé API : 120 requêtes/minute. Pas de limite quotidienne
documentée. Pour un usage semestriel avec quelques dizaines de séries,
on est très loin de cette limite.
"""
import time
import pandas as pd
from fredapi import Fred
from common.config import FRED_API_KEY, get_date_range
from common.cache_utils import merge_incremental, load_cache, get_last_cached_date

_fred_instance = None


def _get_fred():
    global _fred_instance
    if _fred_instance is None:
        if not FRED_API_KEY:
            raise RuntimeError(
                "FRED_API_KEY n'est pas définie. "
                "Fais `export FRED_API_KEY=ta_cle` avant de lancer le script."
            )
        _fred_instance = Fred(api_key=FRED_API_KEY)
    return _fred_instance


def get_series(series_id: str, years: int = None, force_refresh: bool = False) -> pd.DataFrame:
    """
    Récupère une série FRED avec cache incrémental.

    Args:
        series_id: identifiant FRED, ex "FEDFUNDS", "DGS10"
        years: fenêtre en années (défaut = HISTORY_YEARS dans config.py)
        force_refresh: si True, ignore le cache et retélécharge tout

    Returns:
        DataFrame avec colonnes 'date' et 'value', trié par date.
    """
    cache_key = f"fred_{series_id}"

    if force_refresh:
        fred = _get_fred()
        raw = fred.get_series(series_id)
        df = raw.reset_index()
        df.columns = ["date", "value"]
        merge_incremental(cache_key, df)
    else:
        last_date = get_last_cached_date(cache_key)
        fred = _get_fred()
        if last_date is not None:
            # On ne va chercher que les points après la dernière date en cache
            observation_start = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            raw = fred.get_series(series_id, observation_start=observation_start)
        else:
            raw = fred.get_series(series_id)

        if raw is not None and len(raw) > 0:
            df = raw.reset_index()
            df.columns = ["date", "value"]
            merge_incremental(cache_key, df)

        time.sleep(0.1)  # marge de sécurité, largement sous la limite de 120/min

    full_df = load_cache(cache_key)

    if years is not None:
        date_debut, _ = get_date_range(years)
        full_df = full_df[full_df["date"] >= date_debut]

    return full_df.dropna(subset=["value"]).reset_index(drop=True)


def get_multiple_series(series_ids: list, years: int = None) -> dict:
    """Récupère plusieurs séries FRED. Retourne un dict {series_id: DataFrame}."""
    return {sid: get_series(sid, years=years) for sid in series_ids}
