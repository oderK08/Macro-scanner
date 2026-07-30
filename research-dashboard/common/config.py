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
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # optionnelle -- pour le commentaire analytique

if not FRED_API_KEY:
    print("[config] ATTENTION: FRED_API_KEY n'est pas définie (variable d'environnement).")
if not EDGAR_USER_AGENT:
    print("[config] ATTENTION: EDGAR_USER_AGENT n'est pas définie. "
          "La SEC exige un User-Agent identifiable (nom + email).")
if not ANTHROPIC_API_KEY:
    print("[config] INFO: ANTHROPIC_API_KEY n'est pas définie -- le commentaire analytique sera "
          "ignoré, le rapport se limitera aux résumés statiques des README.")

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

# --- Composition du S&P 500 -------------------------------------------------
# Depuis la bascule vers la vraie composition de l'indice (voir
# common/sp500_list.py, qui va chercher la liste à jour sur Wikipedia à
# chaque run), les charts 09/11/12 n'utilisent plus d'échantillon statique
# ici. common/sp500_list.py gère aussi son propre repli en cache local en
# cas d'échec réseau -- voir ce module pour le détail.

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

# --- Groupes pour les charts 13/14 (Debt-to-Assets, Interest Coverage) ------
# Définition alignée sur la terminologie utilisée dans les notes de recherche
# des banques (ex: Wells Fargo Securities) : les 4 "hyperscalers" sont les
# géants du cloud qui construisent leur propre infrastructure IA.
HYPERSCALER_TICKERS = ["MSFT", "GOOGL", "AMZN", "META"]

# "Neoclouds" : fournisseurs de cloud spécialisés IA/GPU, apparus/montés en
# puissance depuis 2023-2024. Catégorie encore récente et en évolution rapide
# -- cette liste demande une révision manuelle plus fréquente que les autres
# listes du projet (voir README du chart 13/14).
#
# Ces entreprises ne font PAS partie du S&P 500 (trop récentes/trop petites en
# capitalisation) donc pas dans common/sp500_list.py -- leur CIK est résolu
# via common.edgar_client.get_ticker_to_cik_map() (fichier officiel SEC).
#
# Point de vigilance : Nebius Group (NBIS) est une société néerlandaise cotée
# au Nasdaq -- elle peut déposer des formulaires différents (20-F/6-K) des
# dépositaires domestiques (10-K/10-Q), avec une couverture EDGAR possiblement
# moins complète/régulière.
NEOCLOUD_TICKERS = ["CRWV", "NBIS", "IREN", "APLD", "CORZ", "WULF", "CIFR"]

# Concepts XBRL pour la dette portant intérêt (composants à ADDITIONNER, pas
# des alternatives -- contrairement aux concepts capex/revenus où un seul
# concept "gagne". La dette totale = portion courante + portion long terme,
# généralement taguées séparément.
DEBT_XBRL_CONCEPTS = ["DebtCurrent", "LongTermDebtNoncurrent"]

# Concepts XBRL candidats pour les charges d'intérêt (fallback). Certaines
# grandes entreprises très peu endettées (ex: hyperscalers avec énormément
# de cash) peuvent cesser de taguer "InterestExpense" isolément une fois la
# charge jugée non significative, et la fondre dans un poste plus large --
# ces concepts alternatifs tentent de capturer ce cas de figure.
INTEREST_EXPENSE_XBRL_CONCEPTS = [
    "InterestExpense",
    "InterestExpenseDebt",
    "InterestAndDebtExpense",
]
