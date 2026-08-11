# Momentum de l'activité US : Chicago Fed National Activity Index

## Séries / source
FRED : `CFNAI` (Federal Reserve Bank of Chicago, mensuel). Indice composite
de 85 indicateurs d'activité US couvrant production, emploi, consommation
et ventes. 0 = croissance au rythme tendanciel.

## Calcul
Série brute en trait fin, moyenne mobile 3 mois (la lecture standard,
dite CFNAI-MA3) en trait principal, calculée localement depuis la série
brute. Seuil historique de récession à -0.70 en pointillés. Garde-fou :
une valeur hors de [-30, 30] fait échouer le chart (le pire de 2020 était
environ -18).

## Pourquoi ce graphique apporte un vrai plus
C'est l'équivalent gratuit d'un score de momentum macro propriétaire :
85 indicateurs agrégés par une Fed régionale en un chiffre comparable sur
50 ans. Là où chaque autre chart du rapport suit UNE série, celui-ci dit
si l'ensemble de l'économie US accélère ou décélère par rapport à sa
tendance — et son seuil de -0.70 sur la MA3 a précédé ou accompagné chaque
récession moderne avec très peu de faux signaux.

## Limitations connues
Publié avec environ trois semaines de décalage et révisé chaque mois
(les 85 composantes sont elles-mêmes révisées). Indice centré sur la
tendance : il mesure l'écart au potentiel, pas le niveau de croissance.
Purement US.
