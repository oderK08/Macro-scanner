# 03 — HY Credit Spread vs S&P 500

## Séries FRED utilisées
- `BAMLH0A0HYM2` : spread High Yield OAS (ICE BofA), quotidien, en points de %
- `SP500` : niveau de l'indice S&P 500, quotidien

## Calcul
Aucune transformation particulière — les deux séries sont affichées
directement, sur deux axes Y séparés (le spread à gauche, l'indice à droite),
alignées par date via `merge_asof` (les deux séries sont quotidiennes mais
pas toujours publiées exactement les mêmes jours).

## Pourquoi ce graphique apporte un vrai plus
Le marché du crédit réagit souvent au risque de défaut **avant** que les
actions ne pricent ce même risque. Le spread HY s'élargit fréquemment 1 à 2
mois avant une correction actions significative. Superposer les deux séries
permet de repérer visuellement ces décalages — un spread qui s'élargit
pendant que les actions montent encore est un signal d'alerte classique
suivi de près par les desks credit.

## Lecture du graphique
- Ligne bleue pleine (axe gauche) : spread HY OAS
- Ligne grise pointillée (axe droit) : niveau S&P 500
- Point + annotation : dernière valeur du spread et son percentile sur la
  fenêtre affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Le S&P 500 est affiché en niveau brut (prix), pas en rendement total —
  donc pas de prise en compte des dividendes réinvestis. Suffisant pour
  repérer visuellement des divergences de timing, pas pour comparer des
  performances.
- `merge_asof` avec tolérance de 5 jours peut occasionnellement associer
  deux points légèrement décalés en cas de jour férié atypique (rare, impact
  négligeable sur la lecture visuelle).
