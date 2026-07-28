# 06 — Chicago Fed National Financial Conditions Index (NFCI)

## Série FRED utilisée
- `NFCI` : indice composite hebdomadaire de la Fed de Chicago

## Calcul
Aucune transformation — la série est déjà un indice composite construit et
publié directement par la Fed de Chicago. Convention de lecture :
- **NFCI = 0** : conditions financières dans la moyenne historique
- **NFCI > 0** : conditions plus restrictives que la moyenne
- **NFCI < 0** : conditions plus accommodantes que la moyenne

## Pourquoi ce graphique apporte un vrai plus
Un seul taux directeur ne dit pas grand-chose sur les conditions
financières réellement vécues par l'économie — accès au crédit, niveau de
levier, volatilité des marchés, spreads de financement, etc. Le NFCI agrège
des dizaines de variables de ce type en un seul indice, ce qui permet de
juger si les conditions sont *réellement* restrictives dans l'économie
réelle, au-delà du simple niveau des taux affiché par la Fed.

## Lecture du graphique
- Ligne bleue : NFCI
- Ligne horizontale grise à 0 : moyenne historique, avec repères "Restrictif
  ↑" / "Accommodant ↓"
- Point + annotation : dernière valeur et son percentile sur la fenêtre
  affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Le NFCI est publié en fréquence hebdomadaire, pas quotidienne ni
  mensuelle — les mouvements très récents (dernières semaines) peuvent
  encore être révisés légèrement par la Fed de Chicago.
- L'indice est une moyenne pondérée de nombreuses variables sous-jacentes ;
  ce chart ne décompose pas quelle composante (crédit, levier, risque...)
  tire l'indice dans un sens ou dans l'autre à un instant donné.
