# 05 — JOLTS Quits Rate vs croissance des salaires

## Séries FRED utilisées
- `JTSQUR` : taux de démission volontaire (Quits Rate), mensuel, %
- `CES0500000003` : salaire horaire moyen, secteur privé, mensuel ($/h)

## Calcul
Le taux de démission (`quits_rate`) est utilisé directement, sans
transformation.

## Pourquoi ce graphique apporte un vrai plus
Les salariés ne démissionnent volontairement que s'ils sont confiants de
retrouver un emploi équivalent ou meilleur ailleurs. Le taux de démission
est donc un indicateur **avancé** de la tension sur le marché du travail —
il précède généralement l'inflation salariale de plusieurs mois,
contrairement au taux de chômage qui réagit plus tardivement. Un quits rate
qui remonte est souvent le signe avant-coureur d'une accélération des
salaires à venir.

## Lecture du graphique
- Ligne bleue pleine (axe gauche) : Quits Rate (%)
- Ligne rouge pointillée (axe droit) : croissance annuelle des salaires (%)
- Point + annotation : dernière valeur du Quits Rate et son percentile sur
  la fenêtre affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- `CES0500000003` mesure le salaire horaire moyen nominal, pas ajusté de
  l'inflation ni de la composition sectorielle de l'emploi (un changement
  de mix d'emplois peut faire bouger la moyenne sans vrai changement de
  pouvoir de négociation des salariés).
- Le lien quits rate → salaires n'est pas un décalage fixe modélisé
  explicitement dans ce chart (contrairement au 04) — il s'agit ici d'une
  superposition brute à lire visuellement, pas d'un décalage temporel
  calculé.
