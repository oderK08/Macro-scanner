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
│   ├── cftc_client.py       # wrapper API CFTC (COT) + rate limiting + cache
│   ├── chart_style.py       # style matplotlib partagé, percentile/z-score
│   └── themes.py            # regroupement thématique des graphiques (pilote l'ordre du rapport PDF)
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
│   ├── 15_central_bank_gold_reserves/          ⚠️ implémenté, source DBnomics non éprouvée — Banques centrales
│   ├── 16_net_liquidity_fed/                   🆕 implémenté, 1er run réel à valider — Politique monétaire
│   ├── 17_yield_curve_slope/                   🆕 implémenté, 1er run réel à valider — Politique monétaire
│   ├── 18_real_yield_breakeven/                🆕 implémenté, 1er run réel à valider — Politique monétaire
│   ├── 19_vix_vs_hy_spread/                    🆕 implémenté, 1er run réel à valider — Crédit & marchés
│   ├── 20_dollar_index_vs_10y_yield/           🆕 implémenté, 1er run réel à valider — Devises & flux globaux
│   ├── 21_mortgage_vs_housing_starts/          🆕 implémenté, 1er run réel à valider — Consommateur / ménages
│   ├── 22_buybacks_vs_capex/                   🆕 implémenté, 1er run réel à valider — Corporate / secteurs
│   ├── 23_net_debt_ebitda_by_sector/           🆕 implémenté, 1er run réel à valider — Corporate / secteurs
│   ├── 24_earnings_growth_vs_price_growth/     🆕 implémenté, 1er run réel à valider — Corporate / secteurs
│   ├── 25_sloos_credit_standards/              🆕 implémenté, 1er run réel à valider — Crédit & marchés
│   ├── 26_federal_interest_burden/             🆕 implémenté, 1er run réel à valider — Budget fédéral & dette US
│   ├── 27_cot_positioning/                     ⚠️ implémenté, source CFTC non éprouvée — Crédit & marchés
│   └── 28_gdpnow_vs_gdp/                       🆕 implémenté, 1er run réel à valider — Cycle & emploi
├── data_cache/               # CSV bruts (cache incrémental, régénérable)
├── output/                  # PNG générés, un sous-dossier par période (2026S2, etc.)
├── run_all.py                # génère tous les graphiques d'un coup
├── generate_commentary.py    # commentaire IA d'interprétation par graphique (API Anthropic, optionnel)
├── compile_report.py         # compile les PNG + commentaires en rapport PDF
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

## Organisation thématique du rapport

Le rapport PDF (`compile_report.py`) regroupe les graphiques par grands
thèmes (politique monétaire, cycle & emploi, crédit & marchés, corporate,
etc.) : sommaire sectionné et bandeau de thème dans le corps du rapport.

Le classement est piloté par **un seul fichier** : `common/themes.py`. Les
noms de dossiers `charts/NN_*` n'encodent aucun thème — reclasser un
graphique ne demande ni renommage de dossier, ni perte de cache. Un
graphique absent de `themes.py` n'est pas perdu : il apparaît en fin de
rapport dans la section « Autres / à classer » (volontairement visible,
pour qu'un oubli de classement saute aux yeux).

## Commentaire IA d'interprétation (generate_commentary.py)

Après la génération des PNG, `generate_commentary.py` envoie chaque
graphique (image + README) à l'API Anthropic et obtient un court paragraphe
d'interprétation de la configuration actuelle : ce que montre le dernier
point, la tendance récente, et ce que ça implique pour le comité. Les
commentaires sont écrits dans `output/{période}/commentary.json`, et le
rapport PDF les affiche **sous le résumé statique du README**, en italique,
avec la mention « Lecture du moment » et la date de génération.

Cet enrichissement est **optionnel et jamais bloquant** : sans la clé
`ANTHROPIC_API_KEY` (secret GitHub), ou si l'API est en panne, le script se
retire proprement et le rapport se limite aux résumés des README. Une
erreur sur un graphique n'empêche pas les autres, et un commentaire déjà
généré n'est jamais écrasé par du vide. Le modèle utilisé (`claude-opus-5`
par défaut) est surchargeable via la variable d'environnement
`COMMENTARY_MODEL`, sans toucher au code.

## Règles de rendu (chart_style.py)

Trois garanties, valables pour tous les graphiques, imposées par
`common/chart_style.py` :

1. **Aucun texte dans la zone de tracé.** Les valeurs des derniers points et
   leurs percentiles vivent dans les labels de légende
   (`format_last_value_label`), la légende est rendue **sous** le graphique
   par `finalize_chart`, et les repères ponctuels (« hors échelle »,
   chiffre-clé) passent par le paramètre `note` de `finalize_chart` — même
   bande basse, hors tracé. Un texte posé au bout d'une courbe finit
   toujours par chevaucher quelque chose pour certaines valeurs futures des
   données — interdit sur un projet qui tourne sans surveillance.
2. **Géométrie unique.** Taille de figure et marges fixes (`FIGSIZE`,
   `_MARGINS`, pas de `tight_layout`) : chaque PNG fait exactement
   1500×945 px avec la zone de tracé au même endroit.
3. **Palette sémantique unique**, par rôle de série (voir le commentaire en
   tête de `chart_style.py`) : bleu marine = série principale, rouge
   brique = deuxième série / seuils d'alerte, bleu clair = troisième série,
   gris pointillé = série de référence/contexte, `tab20` pour le
   catégoriel (secteurs, tickers, pays).

## Ajouter un nouveau graphique

1. Créer `charts/NN_nom_du_graphique/`
2. Copier la structure de `charts/02_sahm_rule/generate.py` comme modèle
3. Utiliser `common/fred_client.py` et/ou `common/edgar_client.py` pour les
   données, `common/chart_style.py` pour le rendu — en respectant les trois
   règles ci-dessus (terminer par `finalize_chart`, jamais de `ax.legend`
   ni de `ax.annotate`/`ax.text` dans la zone de tracé)
4. Documenter dans le `README.md` du dossier : séries, calcul, utilité,
   limitations
5. Le rattacher à un thème dans `common/themes.py` (sinon il sortira dans
   « Autres / à classer » en fin de rapport)
6. `run_all.py` le détectera automatiquement au prochain run

## Notes sur les révisions de données

Certaines séries macro (PIB, PCE...) sont révisées après publication. Ce
projet utilise systématiquement la valeur la plus récente connue (pas la
valeur "vintage" telle que publiée à l'époque, qui nécessiterait ALFRED
plutôt que FRED). Choix pris pour la simplicité — à garder en tête si tu
compares avec des publications historiques figées.
