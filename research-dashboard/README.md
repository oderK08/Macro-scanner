# Research Dashboard

Génération automatisée de graphiques macro/micro-économiques façon "recherche
de banque d'investissement", à partir de sources 100% gratuites (FRED, SEC
EDGAR). Conçu pour être relancé à intervalle régulier (semestriel) avec une
fenêtre glissante de 10 ans d'historique.

## Structure du projet

```
research-dashboard/
├── common/                  # code partagé (clients API, cache, style)
│   ├── config.py            # clés API, fenêtre temporelle, listes de référence
│   ├── cache_utils.py       # cache local incrémental (CSV)
│   ├── fred_client.py       # wrapper FRED + cache
│   ├── edgar_client.py      # wrapper SEC EDGAR + rate limiting + cache
│   └── chart_style.py       # style matplotlib partagé, percentile/z-score
├── charts/                  # un dossier par graphique
│   ├── 01_real_fed_funds_rate/                ✅ implémenté — Politique monétaire
│   ├── 02_sahm_rule/                           ✅ implémenté — Cycle & emploi
│   ├── 03_hy_credit_spread_vs_sp500/           ✅ implémenté — Crédit & marchés
│   ├── 04_m2_vs_cpi_lag/                       ✅ implémenté — Inflation & monnaie
│   ├── 05_jolts_quits_vs_wages/                ✅ implémenté — Cycle & emploi
│   ├── 06_nfci_financial_conditions/           ✅ implémenté — Politique monétaire
│   ├── 07_term_premium_10y/                    ✅ implémenté — Politique monétaire
│   ├── 08_debt_service_vs_savings/             ✅ implémenté — Consommateur / ménages
│   ├── 09_capex_sp500_aggregate/               ✅ implémenté — Corporate / secteurs
│   ├── 10_capex_guidance_revisions_megacaps/   ✅ implémenté — Corporate / IA-capex
│   ├── 11_sector_operating_margins/            ✅ implémenté — Corporate / secteurs
│   ├── 12_inventory_to_sales_ratio/            ✅ implémenté — Corporate / secteurs
│   ├── 13_debt_to_assets_by_group/             ✅ implémenté — Corporate / IA-capex
│   └── 15_central_bank_gold_reserves/          ⚠️ implémenté, source DBnomics non éprouvée — Banques centrales
├── data_cache/               # CSV bruts (cache incrémental, régénérable)
├── output/                  # PNG générés, un sous-dossier par période (2026S2, etc.)
├── run_all.py                # génère tous les graphiques d'un coup
├── requirements.txt
├── .env.example
└── .gitignore
```

Chaque dossier de `charts/` contient :
- `generate.py` : le code qui récupère les données, calcule, trace, sauvegarde
- `README.md` : quelles séries, quel calcul, pourquoi c'est utile, limitations

## Installation

```bash
git clone <ton-repo>
cd research-dashboard
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt

cp .env.example .env
# édite .env avec ta clé FRED et ton User-Agent EDGAR
```

Récupérer une clé FRED (gratuit, instantané) : https://fredaccount.stlouisfed.org

Charger les variables d'environnement avant de lancer :
```bash
export $(grep -v '^#' .env | xargs)   # macOS/Linux
```

## Lancer le projet

Un seul graphique :
```bash
python charts/01_real_fed_funds_rate/generate.py
```

Tous les graphiques d'un coup :
```bash
python run_all.py
```

Les PNG sortent dans `output/{période}/`, ex. `output/2026S2/01_real_fed_funds_rate.png`.

## Fenêtre glissante & cache incrémental

- **Fenêtre glissante** : chaque graphique calcule sa fenêtre "aujourd'hui - 10
  ans" dynamiquement (`common/config.py::get_date_range`). Pas de date en dur —
  relancer le projet dans 6 mois ou 3 ans ne demande aucune modification.
- **Cache incrémental** : `data_cache/*.csv` stocke l'historique déjà
  téléchargé. À chaque run, seuls les points manquants (depuis la dernière
  date en cache) sont re-téléchargés, puis fusionnés. Ça rend chaque run
  rapide et limite l'usage des API.

## Limites des API (gratuites, mais pas illimitées)

- **FRED** : 120 requêtes/minute avec clé API, pas de limite quotidienne
  documentée. Largement suffisant pour un usage semestriel.
- **SEC EDGAR** : 10 requêtes/seconde par IP (limite stricte). Le client
  (`common/edgar_client.py`) se cale à ~5/s par sécurité. User-Agent
  identifiable (nom + email) obligatoire sur chaque requête.

## Ajouter un nouveau graphique

1. Créer `charts/NN_nom_du_graphique/`
2. Copier la structure de `charts/02_sahm_rule/generate.py` comme modèle
3. Utiliser `common/fred_client.py` et/ou `common/edgar_client.py` pour les
   données, `common/chart_style.py` pour le rendu
4. Documenter dans le `README.md` du dossier : séries, calcul, utilité,
   limitations
5. `run_all.py` le détectera automatiquement au prochain run

## Notes sur les révisions de données

Certaines séries macro (PIB, PCE...) sont révisées après publication. Ce
projet utilise systématiquement la valeur la plus récente connue (pas la
valeur "vintage" telle que publiée à l'époque, qui nécessiterait ALFRED
plutôt que FRED). Choix pris pour la simplicité — à garder en tête si tu
compares avec des publications historiques figées.
