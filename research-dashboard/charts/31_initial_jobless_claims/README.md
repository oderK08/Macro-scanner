# Marché du travail en temps réel : inscriptions hebdomadaires au chômage

## Séries / source
FRED : `ICSA` (US Employment and Training Administration). Nouvelles
demandes d'allocations chômage, hebdomadaire, désaisonnalisé, publiées
chaque jeudi pour la semaine précédente — la donnée macro la plus rapide
du rapport.

## Calcul
Série brute en trait fin, moyenne mobile 4 semaines (lecture standard,
gomme le bruit des jours fériés) en trait principal, en milliers de
personnes. Échelle logarithmique : le pic COVID (~6 100k) écraserait sinon
la plage normale (150-450k) où vivent les signaux. Garde-fou : une valeur
hors de [50k, 10M] fait échouer le chart.

## Pourquoi ce graphique apporte un vrai plus
Les claims se retournent avant le taux de chômage : c'est l'indicateur
avancé de notre indicateur avancé (la règle de Sahm, chart 02). Une dérive
soutenue de la moyenne 4 semaines au-dessus de ses plus bas est
historiquement le premier signal dur de retournement du marché du travail,
avec des mois d'avance sur les données mensuelles. Entre deux comités,
c'est la série à re-regarder chaque semaine.

## Limitations connues
Série bruitée (jours fériés, grèves, intempéries) — d'où la MA4. La
désaisonnalisation est périodiquement re-calibrée. Le niveau "normal"
dérive avec la taille de la population active : comparer aux dernières
années, pas aux années 1980.
