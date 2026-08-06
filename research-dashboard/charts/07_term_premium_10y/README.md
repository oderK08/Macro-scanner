# Term Premium 10 ans (modèle Kim-Wright, Fed Board)

## Séries / source
FRED : `THREEFYTP10` (term premium 10 ans, modèle Kim-Wright du Federal
Reserve Board, quotidien) et `DGS10` (taux nominal 10 ans, quotidien).

## Pourquoi ce graphique apporte un vrai plus
Le rendement 10 ans se décompose en deux éléments : la moyenne des taux
courts anticipés, et une prime de risque (term premium) exigée pour détenir
du long plutôt que rouler du court. Une hausse du 10 ans tirée par la prime
(aversion au risque, incertitude budgétaire, offre de dette) ne raconte pas
la même histoire qu'une hausse tirée par les anticipations de croissance ou
d'inflation.

## Limitations connues
Ce n'est pas le modèle ACM de la NY Fed (le plus cité par les banques),
absent de FRED — la première version du chart visait `ACMTP10` et échouait
pour cette raison. Kim-Wright est comparable (corrélation ~0.86 sur 35 ans)
mais pas identique. Le term premium est une estimation économétrique,
révisable si le modèle est recalibré, et peut être durablement négatif
(décennie 2010) sans que ce soit une anomalie.
