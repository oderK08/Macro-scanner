"""
Configuration centrale du projet.

Toutes les clés API et paramètres sensibles se chargent depuis des
variables d'environnement (jamais en dur dans le code, jamais commit sur GitHub).

Usage local :
    export FRED_API_KEY="ta_cle"
    export EDGAR_USER_AGENT="Prenom Nom ton.email@exemple.com"

Ou via un fichier .env (voir .env.example à la racine).
"""
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

# --- Clés / identifiants ---------------------------------------------------
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
EDGAR_USER_AGENT = os.environ.get("EDGAR_USER_AGENT", "")  # ex: "Jean Dupont jean.dupont@email.com"

if not FRED_API_KEY:
    print("[config] ATTENTION: FRED_API_KEY n'est pas définie (variable d'environnement).")
if not EDGAR_USER_AGENT:
    print("[config] ATTENTION: EDGAR_USER_AGENT n'est pas définie. "
          "La SEC exige un User-Agent identifiable (nom + email).")

# --- Fenêtre temporelle glissante -------------------------------------------
# Toujours calculée dynamiquement par rapport à aujourd'hui : jamais de date
# en dur. Ça permet de relancer le projet dans 6 mois, 2 ans, 10 ans, sans
# avoir à toucher au code.
HISTORY_YEARS = 10

def get_date_range(years: int = HISTORY_YEARS):
    """Retourne (date_debut, date_fin) au format YYYY-MM-DD, fenêtre glissante."""
    date_fin = datetime.today()
    date_debut = date_fin - relativedelta(years=years)
    return date_debut.strftime("%Y-%m-%d"), date_fin.strftime("%Y-%m-%d")

# --- Périodicité de run (semestriel) ---------------------------------------
# Utilisé uniquement pour nommer les dossiers de sortie (output/2026S2, etc.)
def get_current_period_label():
    now = datetime.today()
    semestre = 1 if now.month <= 6 else 2
    return f"{now.year}S{semestre}"

# --- Chemins -----------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CACHE_DIR = os.path.join(PROJECT_ROOT, "data_cache")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# --- Listes de référence -----------------------------------------------------
# Mega-caps suivies pour le suivi de guidance capex (chart 10).
# À ajuster librement — ce sont les boîtes qui communiquent le plus clairement
# leur capex prévisionnel dans leurs communiqués / 10-Q.
MEGACAP_CAPEX_TICKERS = ["MSFT", "META", "GOOGL", "AMZN", "AAPL"]

# Concepts XBRL candidats pour le capex (ordre = ordre de préférence/fallback).
# Toutes les entreprises ne taguent pas leur capex de la même façon.
CAPEX_XBRL_CONCEPTS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsForCapitalImprovements",
    "PaymentsToAcquireProductiveAssets",
]

# Échantillon statique de grandes capitalisations US, organisé par secteur.
# Il n'existe PAS de liste "S&P 500" directement interrogeable sur EDGAR --
# on utilise donc une liste maintenue à la main.
#
# IMPORTANT : ceci est un échantillon représentatif de grandes capitalisations
# réparties sur plusieurs secteurs, PAS la liste exacte et à jour des 500
# constituants du S&P 500. La composition du S&P 500 change plusieurs fois
# par an (ajouts/retraits) ; cette liste n'est pas synchronisée
# automatiquement avec ces changements. À réviser/étoffer manuellement de
# temps en temps si tu veux affiner la couverture -- voir les README des
# charts 09/11/12 pour le détail de cette limitation.
SECTOR_TICKERS = {
    "Technologie": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL", "CSCO", "IBM",
                    "INTC", "ADBE", "CRM", "AVGO"],
    "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK"],
    "Santé": ["JNJ", "PFE", "UNH", "MRK", "ABBV", "TMO", "ABT"],
    "Industrie": ["BA", "CAT", "GE", "HON", "UPS", "LMT", "RTX", "MMM"],
    "Énergie": ["XOM", "CVX", "COP", "SLB"],
    "Consommation": ["WMT", "PG", "KO", "PEP", "MCD", "NKE", "HD", "COST", "DIS"],
    "Télécoms": ["T", "VZ"],
    "Utilities": ["NEE", "DUK"],
}

# Liste plate dérivée de SECTOR_TICKERS -- utilisée par le chart 09 (capex
# agrégé) qui n'a pas besoin de la distinction par secteur.
SP500_LARGE_CAP_SAMPLE = [ticker for tickers in SECTOR_TICKERS.values() for ticker in tickers]

# Concepts XBRL candidats pour le chiffre d'affaires (fallback, comme pour le
# capex -- toutes les entreprises ne taguent pas leurs revenus pareil).
REVENUE_XBRL_CONCEPTS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
]

# Concept XBRL pour le résultat opérationnel (généralement stable d'une
# entreprise à l'autre, moins besoin de fallback que revenus/capex).
OPERATING_INCOME_XBRL_CONCEPTS = ["OperatingIncomeLoss"]

# Concepts XBRL candidats pour les stocks/inventaires (poste de bilan, donc
# concept "instant", pas "duration" -- voir chart 12 pour la nuance de format
# de période EDGAR que ça implique).
INVENTORY_XBRL_CONCEPTS = ["InventoryNet"]
