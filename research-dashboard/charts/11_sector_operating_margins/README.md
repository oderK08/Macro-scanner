# 11 — Marges opérationnelles par secteur

## Source
SEC EDGAR, endpoint `frames`.

## Concepts XBRL utilisés
- **Revenus** (fallback) : `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`
- **Résultat opérationnel** : `OperatingIncomeLoss`

## Calcul
Pour chaque secteur (`common.config.SECTOR_TICKERS`), chaque trimestre :
1. Somme du chiffre d'affaires et du résultat opérationnel de toutes les
   entreprises du secteur trouvées dans les données EDGAR ce trimestre-là
2. Chaque somme est convertie en TTM (glissant sur 4 trimestres), pour
   lisser la saisonnalité (ex: la distribution a un gros T4 chaque année à
   cause des fêtes, sans lissage la marge sectorielle ferait des dents de
   scie artificielles)
3. `marge = résultat_opérationnel_TTM / chiffre_affaires_TTM * 100`

## Pourquoi ce graphique apporte un vrai plus
La compression ou l'expansion de marge sectorielle révèle si le pouvoir de
fixation des prix (pricing power) d'un secteur entier s'érode — une marge
qui baisse malgré des revenus stables ou en hausse suggère une pression
concurrentielle ou des coûts qui montent plus vite que les prix de vente.
C'est une lecture agrégée que les chiffres d'une seule entreprise ne
permettent pas : une marge en baisse chez une entreprise peut être
spécifique à elle, mais si c'est tout un secteur, c'est un vrai signal
macro/sectoriel.

## Secteurs suivis
Technologie, Finance, Santé, Industrie, Énergie, Consommation, Télécoms,
Utilities — voir `common.config.SECTOR_TICKERS` pour la composition exacte
de chaque secteur.

## Lecture du graphique
- Une ligne par secteur, couleur distincte
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Même limitation d'échantillon que les charts 09/10 : ce sont des listes
  statiques de grandes capitalisations par secteur, pas la composition
  exacte et à jour des indices sectoriels officiels (GICS, etc.)
- Un secteur peut être dominé par 1-2 très grandes entreprises dans
  l'échantillon (ex: la Tech est tirée par les résultats d'Apple/Microsoft/
  Google plus que par la moyenne du secteur) — la marge "sectorielle"
  affichée est en réalité pondérée par la taille des entreprises, pas une
  moyenne simple par entreprise.
- Les exercices fiscaux décalés entre entreprises d'un même secteur peuvent
  introduire un léger désalignement trimestriel (même nuance que le
  chart 09).
