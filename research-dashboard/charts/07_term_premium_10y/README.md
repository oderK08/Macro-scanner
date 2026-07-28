# 07 — Term Premium 10 ans (décomposition NY Fed ACM)

## Séries FRED utilisées
- `ACMTP10` : term premium à 10 ans, modèle ACM de la NY Fed, quotidien
- `DGS10` : taux nominal du Trésor US à 10 ans, quotidien

## Calcul
Aucune transformation — les deux séries sont affichées directement.

## Pourquoi ce graphique apporte un vrai plus
Le rendement à 10 ans se décompose en deux éléments : (1) la moyenne des
taux courts anticipés sur les 10 prochaines années, et (2) une prime de
risque (term premium) que les investisseurs exigent pour détenir une
obligation longue plutôt que de rouler des obligations courtes. Une hausse
du taux 10 ans tirée par la prime de risque (aversion au risque,
incertitude budgétaire, offre de dette) ne raconte pas la même histoire
économique qu'une hausse tirée par les anticipations de croissance ou
d'inflation. C'est un chart classique des desks *rates* dans les notes de
recherche des banques d'investissement.

## Lecture du graphique
- Ligne grise pointillée : taux nominal 10 ans (DGS10)
- Ligne bleue pleine : term premium (ACMTP10)
- Point + annotation : dernière valeur du term premium et son percentile
  sur la fenêtre affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Le modèle ACM (Adrian-Crump-Moench) est une estimation économétrique, pas
  une donnée observée directement — elle peut être révisée rétroactivement
  par la NY Fed si le modèle est recalibré.
- Le term premium peut être négatif (ce qui a été le cas une bonne partie
  de la décennie 2010) : ce n'est pas une anomalie, juste une conséquence
  du contexte de taux bas et d'assouplissement quantitatif.
