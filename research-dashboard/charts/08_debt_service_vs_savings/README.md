# 08 — Debt Service Ratio vs Taux d'épargne des ménages

## Séries FRED utilisées
- `TDSP` : Household Debt Service Ratio, trimestriel, %
- `PSAVERT` : Personal Saving Rate, mensuel, %

## Calcul
Aucune transformation — les deux séries sont affichées directement, sur
deux axes Y séparés, alignées par date via `merge_asof` (tolérance de 100
jours pour concilier la fréquence trimestrielle de TDSP et mensuelle de
PSAVERT).

## Pourquoi ce graphique apporte un vrai plus
Ce chart aide à distinguer deux scénarios très différents pour la
consommation des ménages américains :
- Si la consommation tient **et** que le debt service ratio reste bas
  **et** que le taux d'épargne est stable ou en hausse → les ménages sont
  globalement sains, la consommation repose sur des bases solides.
- Si la consommation tient uniquement parce que le taux d'épargne
  s'effondre (les ménages puisent dans leurs réserves) ou que le debt
  service ratio grimpe (endettement croissant pour maintenir le niveau de
  vie) → la situation est plus fragile et moins soutenable dans la durée.

## Lecture du graphique
- Ligne bleue pleine (axe gauche) : Debt Service Ratio (%)
- Ligne rouge pointillée (axe droit) : taux d'épargne (%)
- Point + annotation : dernière valeur du Debt Service Ratio et son
  percentile sur la fenêtre affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Le pic massif du taux d'épargne en 2020-2021 (transferts Covid) déforme
  fortement l'échelle et les percentiles sur 10 ans — à garder en tête pour
  ne pas sur-interpréter les niveaux "normaux" actuels par rapport à cette
  période exceptionnelle.
- `TDSP` est un ratio agrégé national ; il ne dit rien de la répartition du
  risque entre ménages (un debt service ratio agrégé bas peut masquer une
  poche de ménages très endettés).
