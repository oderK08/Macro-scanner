"""
Cache local incrémental.

Principe : chaque série/concept est stocké dans un CSV sous data_cache/.
Au lieu de re-télécharger tout l'historique à chaque run, on ne va chercher
sur l'API que les points manquants (après la dernière date en cache), puis
on fusionne (merge) avec l'existant.

Ça rend chaque run semestriel rapide et évite de solliciter les API pour
des données qui ne bougent de toute façon plus.
"""
import os
import pandas as pd
from common.config import DATA_CACHE_DIR

os.makedirs(DATA_CACHE_DIR, exist_ok=True)


def _cache_path(key: str) -> str:
    safe_key = key.replace("/", "_")
    return os.path.join(DATA_CACHE_DIR, f"{safe_key}.csv")


def load_cache(key: str) -> pd.DataFrame:
    """Charge le cache existant pour une clé donnée. Retourne un DataFrame vide si absent."""
    path = _cache_path(key)
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["date"])
        return df.sort_values("date").reset_index(drop=True)
    return pd.DataFrame(columns=["date", "value"])


def save_cache(key: str, df: pd.DataFrame):
    """Sauvegarde (écrase) le cache pour une clé donnée. df doit avoir les colonnes date/value."""
    path = _cache_path(key)
    df = df.sort_values("date").drop_duplicates(subset="date", keep="last")
    df.to_csv(path, index=False)


def merge_incremental(key: str, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les nouvelles données avec le cache existant et sauvegarde.
    new_df doit avoir les colonnes 'date' (datetime) et 'value'.
    Retourne le DataFrame fusionné complet.
    """
    existing = load_cache(key)
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    combined = combined.sort_values("date").drop_duplicates(subset="date", keep="last")
    save_cache(key, combined)
    return combined


def get_last_cached_date(key: str):
    """Retourne la dernière date en cache pour cette clé, ou None si le cache est vide."""
    df = load_cache(key)
    if df.empty:
        return None
    return df["date"].max()
