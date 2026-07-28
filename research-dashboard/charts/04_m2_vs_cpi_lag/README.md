# 04 — M2 YoY vs CPI YoY (décalé de 15 mois)

## Séries FRED utilisées
- `M2SL` : masse monétaire M2, mensuel
- `CPIAUCSL` : indice des prix à la consommation (CPI), mensuel

## Calcul

Le lag de 15 mois est un choix au milieu de la fourchette 12-18 mois
généralement citée dans la littérature monétariste — modifiable via la
constante `LAG_MONTHS` en haut de `generate.py`.

## Pourquoi ce graphique apporte un vrai plus
La théorie quantitative de la monnaie prédit qu'une accélération de la
masse monétaire se traduit en inflation avec un délai, pas immédiatement.
Ce décalage explique une bonne partie de la trajectoire de l'inflation
2021-2023 avant même que les chiffres officiels de CPI ne l'aient révélé.
En superposant les deux séries avec le bon décalage, on peut visuellement
juger si la relation continue de tenir ou si elle s'est rompue.

## Lecture du graphique
- Ligne bleue pleine : M2 YoY (%)
- Ligne rouge pointillée : CPI YoY (%), décalé de 15 mois vers la gauche
- Si les deux lignes se superposent bien, le lag monétariste "tient" sur la
  période ; un décrochage visible indique que la relation s'est affaiblie
  ou que d'autres facteurs dominent (chocs d'offre, politique budgétaire...)

## Limitations connues
- Le lag de 15 mois est une approximation fixe, pas ré-estimée
  statistiquement à chaque run (pas de calcul de corrélation croisée pour
  trouver le lag optimal — volontairement simple pour rester lisible).
- La relation M2→CPI a été historiquement moins stable depuis 2020
  (distorsions Covid, chocs d'offre) — ce chart montre la théorie, pas une
  prédiction fiable en toute circonstance.
