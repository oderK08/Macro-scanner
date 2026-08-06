# Debt Service Ratio vs Taux d'épargne des ménages

## Séries / source
FRED : `TDSP` (Household Debt Service Ratio, trimestriel) et `PSAVERT`
(Personal Saving Rate, mensuel). Deux axes Y, alignement par `merge_asof`
avec tolérance de 100 jours pour concilier les deux fréquences.

## Pourquoi ce graphique apporte un vrai plus
Il distingue deux scénarios opposés pour la consommation américaine : une
consommation qui tient avec un service de la dette bas et une épargne
stable repose sur des bases saines ; une consommation qui ne tient que
parce que l'épargne s'effondre ou que l'endettement grimpe est fragile et
peu soutenable.

## Limitations connues
Le pic d'épargne 2020-2021 (transferts Covid) déforme l'échelle et les
percentiles sur 10 ans. `TDSP` est un agrégat national qui ne dit rien de
la répartition du risque entre ménages.
