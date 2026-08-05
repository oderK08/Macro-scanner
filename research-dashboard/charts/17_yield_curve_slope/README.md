# 17 — Pente de la courbe des taux US (2s10s et 3m10y)

## Séries FRED utilisées
- `T10Y2Y` : écart 10 ans − 2 ans du Trésor US, quotidien, points de %
- `T10Y3M` : écart 10 ans − 3 mois du Trésor US, quotidien, points de %

Ce sont des **spreads déjà calculés et publiés par FRED** — pas de
soustraction manuelle de deux séries de taux, donc pas de risque d'erreur
d'alignement de dates.

## Calcul
Aucune transformation — les deux spreads sont affichés directement, avec
une ligne zéro (sous laquelle la courbe est inversée) et les bandes de
récession NBER en fond.

## Pourquoi ce graphique apporte un vrai plus
L'inversion de la courbe des taux est l'indicateur avancé de récession le
plus documenté de la littérature : chaque récession US depuis les années
1960 a été précédée d'une inversion, avec un délai typique de **6 à 24
mois**. Le 3m10y est la variante préférée de la recherche académique
(Estrella & Mishkin) et du modèle de probabilité de récession de la Fed de
New York ; le 2s10s est la variante la plus suivie par les marchés. Les
afficher ensemble évite de se raconter une histoire sur la base d'une seule
des deux — elles peuvent diverger (le 3m10y dépend surtout du taux
directeur courant, le 2s10s des anticipations).

Complémentarité avec le chart 02 (Sahm Rule) : la courbe est un signal de
**marché**, en avance de plusieurs trimestres ; la Sahm Rule est un signal
d'**emploi**, quasi coïncident. Courbe inversée + Sahm déclenchée = faisceau
d'indices convergent.

## Lecture du graphique
- Sous la ligne pointillée zéro : courbe inversée
- Attention au piège classique : historiquement, la récession arrive
  souvent **après la re-pentification** (dés-inversion), pas pendant
  l'inversion elle-même

## Limitations connues
- Faux signal notable : l'inversion 2022-2024 a été la plus longue de
  l'histoire sans récession déclarée à ce jour — le QE/QT et la
  distorsion du term premium (voir chart 07) ont pu affaiblir le signal.
- Le délai signal → récession est très variable (6 à 24 mois) : l'inversion
  dit "risque élevé devant", pas "récession au trimestre T".
