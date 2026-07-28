# 09 — Capex agrégé (échantillon de grandes capitalisations US)

## Source
SEC EDGAR, endpoint `frames` — récupère un concept XBRL donné pour **toutes**
les entreprises qui le publient, sur un trimestre donné, en un seul appel
API (bien plus efficace que d'interroger CIK par CIK).

## Concepts XBRL utilisés (avec fallback)
1. `PaymentsToAcquirePropertyPlantAndEquipment`
2. `PaymentsForCapitalImprovements`
3. `PaymentsToAcquireProductiveAssets`

Le script essaie ces concepts dans l'ordre pour chaque trimestre et prend
le premier qui renvoie des données (certaines entreprises taguent leur
capex différemment selon les concepts XBRL disponibles).

## Calcul
Pour chaque trimestre des `HISTORY_YEARS` dernières années :
1. Appel `frames` pour récupérer le concept capex pour toutes les
   entreprises qui l'ont publié ce trimestre-là
2. Filtrage sur les CIK correspondant à `SP500_LARGE_CAP_SAMPLE`
   (voir `common/config.py`)
3. Somme des valeurs -> capex total agrégé du trimestre, converti en
   milliards de USD

## ⚠️ Limitation majeure — à bien comprendre avant d'interpréter ce chart
**Ce graphique n'utilise PAS la liste exacte et à jour des 500 constituants
du S&P 500.** Il n'existe aucun moyen d'interroger EDGAR pour obtenir "la
composition actuelle du S&P 500" — cette information n'est pas publiée par
la SEC. `SP500_LARGE_CAP_SAMPLE` (dans `common/config.py`) est une liste
statique d'une quarantaine de grandes capitalisations US, maintenue à la
main, choisie pour représenter plusieurs secteurs (tech, finance, santé,
industrie, énergie, consommation, télécoms, utilities) — **pas la liste
officielle et exhaustive de l'indice**.

Concrètement :
- Le total affiché est un **ordre de grandeur représentatif**, pas le vrai
  total exact du S&P 500
- La composition du S&P 500 change plusieurs fois par an (ajouts/retraits) ;
  cette liste n'est **pas synchronisée automatiquement** avec ces
  changements
- Si tu veux affiner la couverture, tu peux éditer `SP500_LARGE_CAP_SAMPLE`
  à la main dans `common/config.py` pour ajouter/retirer des tickers

## Pourquoi ce graphique apporte un vrai plus malgré cette limitation
Le capex agrégé des grandes entreprises US est un indicateur avancé du
cycle d'investissement — particulièrement suivi actuellement avec
l'explosion des dépenses d'infrastructure IA chez les hyperscalers
(Microsoft, Meta, Amazon, Google, qui pèsent une part disproportionnée du
capex agrégé). Même un échantillon de grandes capitalisations, pas
l'indice exact, capture bien cette dynamique puisque le capex global est
très concentré sur un petit nombre d'acteurs.

## Lecture du graphique
- Ligne bleue avec marqueurs : capex trimestriel agrégé (milliards USD) de
  l'échantillon suivi
- Point + annotation : dernier trimestre disponible, montant total, et
  nombre d'entreprises ayant effectivement publié ce trimestre-là

## Limitations connues (en plus de celle ci-dessus)
- Les exercices fiscaux décalés (ex: Apple termine son année fiscale en
  septembre) signifient que "le T3 calendaire" ne correspond pas au même
  trimestre fiscal pour toutes les entreprises — les totaux trimestriels
  mélangent donc des périodes fiscales légèrement désynchronisées.
- Un trimestre est exclu du graphique si moins de la moitié des tickers
  suivis ont publié leurs données à ce moment du run (couverture
  insuffisante) — voir `min_companies` dans `generate.py`.
- Pas d'ajustement pour les fusions/acquisitions/spin-offs parmi les
  tickers suivis au fil du temps.
