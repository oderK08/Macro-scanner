# M2 YoY vs CPI YoY (décalé de 15 mois)

## Séries / source
FRED : `M2SL` (masse monétaire M2, mensuel) et `CPIAUCSL` (CPI, mensuel).

## Calcul
Variation annuelle des deux séries ; la courbe CPI est décalée de 15 mois
(milieu de la fourchette 12-18 mois de la littérature monétariste,
modifiable via `LAG_MONTHS` dans `generate.py`).

## Pourquoi ce graphique apporte un vrai plus
La théorie quantitative de la monnaie prédit qu'une accélération de la
masse monétaire se traduit en inflation avec un délai. Ce décalage explique
une bonne partie de la trajectoire d'inflation 2021-2023 avant les chiffres
officiels ; la superposition permet de juger si la relation tient encore ou
si elle s'est rompue.

## Limitations connues
Le lag de 15 mois est une approximation fixe, pas ré-estimée
statistiquement à chaque run. La relation M2-CPI est moins stable depuis
2020 (chocs d'offre, politique budgétaire) — ce chart montre la théorie,
pas une prédiction fiable en toute circonstance.
