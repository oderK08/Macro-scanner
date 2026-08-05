"""
Regroupement thématique des graphiques du dashboard.

Le tri par thème est piloté depuis ce seul fichier -- ni les noms de
dossiers dans charts/, ni run_all.py, ni le cache incrémental (indexé par
nom de dossier) n'ont besoin de changer. Ça permet de reclasser, réordonner
ou ajouter un graphique à un thème sans toucher à son code ni casser son
historique de cache.

Pour ajouter un nouveau graphique à un thème existant (ou en créer un) :
ajouter son nom de dossier (ex: "25_nouveau_graphique") dans la liste du
thème concerné ci-dessous. Un graphique qui existe dans charts/ mais
n'apparaît dans aucune liste ci-dessous n'est PAS perdu silencieusement :
compile_report.py le fait apparaître automatiquement dans le thème de
secours FALLBACK_THEME en fin de rapport -- volontairement visible, pour
qu'un oubli de classement saute aux yeux au lieu de disparaître du rapport.
"""

THEMES = [
    ("Politique monétaire & conditions financières", [
        "01_real_fed_funds_rate",
        "06_nfci_financial_conditions",
        "07_term_premium_10y",
        "16_net_liquidity_fed",
        "17_yield_curve_slope",
        "18_real_yield_breakeven",
    ]),
    ("Cycle & marché du travail", [
        "02_sahm_rule",
        "05_jolts_quits_vs_wages",
    ]),
    ("Inflation & masse monétaire", [
        "04_m2_vs_cpi_lag",
    ]),
    ("Crédit & marchés actions", [
        "03_hy_credit_spread_vs_sp500",
        "19_vix_vs_hy_spread",
    ]),
    ("Devises & flux globaux", [
        "20_dollar_index_vs_10y_yield",
    ]),
    ("Consommateur & ménages", [
        "08_debt_service_vs_savings",
        "21_mortgage_vs_housing_starts",
    ]),
    ("Corporate & secteurs (S&P 500)", [
        "09_capex_sp500_aggregate",
        "11_sector_operating_margins",
        "12_inventory_to_sales_ratio",
        "22_buybacks_vs_capex",
        "23_net_debt_ebitda_by_sector",
        "24_earnings_growth_vs_price_growth",
    ]),
    ("Boom IA : Hyperscalers & Neoclouds", [
        "10_capex_guidance_revisions_megacaps",
        "13_debt_to_assets_by_group",
    ]),
    ("Banques centrales & réserves", [
        "15_central_bank_gold_reserves",
    ]),
]

FALLBACK_THEME = "Autres / à classer"


def ordered_chart_dirs(existing_chart_dirs):
    """
    Retourne une liste de tuples (theme, chart_dir) dans l'ordre
    d'affichage voulu : thèmes dans l'ordre défini dans THEMES ci-dessus,
    graphiques dans l'ordre listé au sein de chaque thème.

    Les dossiers présents dans existing_chart_dirs mais absents de THEMES
    sont ajoutés en fin de liste sous FALLBACK_THEME (triés
    alphabétiquement) -- jamais perdus silencieusement, jamais besoin de
    modifier ce fichier pour qu'un nouveau graphique reste visible dans le
    rapport, même mal classé.

    Args:
        existing_chart_dirs: itérable des noms de dossiers réellement
            présents dans charts/ (ex: sortie de os.listdir filtrée).
    """
    existing = set(existing_chart_dirs)
    classified = set()
    ordered = []

    for theme_name, chart_dirs in THEMES:
        for chart_dir in chart_dirs:
            if chart_dir in existing:
                ordered.append((theme_name, chart_dir))
                classified.add(chart_dir)

    unclassified = sorted(existing - classified)
    for chart_dir in unclassified:
        ordered.append((FALLBACK_THEME, chart_dir))

    return ordered
