# Ratio inventaires/ventes par secteur

## Séries / source
SEC EDGAR, endpoint `frames`. Inventaires : `InventoryNet`, poste de bilan
« instant » — le format de période EDGAR prend un « I » final
(`CY2025Q2I`), contrairement aux concepts de flux ; l'oublier renvoie une
frame vide sans message d'erreur. Revenus avec fallback (mêmes concepts que
le chart des marges).

## Calcul
Inventaires de fin de trimestre rapportés au chiffre d'affaires TTM,
exprimés en % du chiffre d'affaires annuel immobilisé en stock. Secteurs
sans stocks au sens classique (Finance, Utilities, télécoms) exclus.

## Pourquoi ce graphique apporte un vrai plus
Le ratio inventaires/ventes est un précurseur classique des cycles
industriels et retail : en fin de cycle, les entreprises sur-anticipent la
demande et accumulent du stock invendu (ratio qui monte) ; un ratio qui
redescend après épuisement des stocks précède le restockage de début de
cycle.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement, ratio pondéré
par la taille des entreprises. Les modes de gestion de stock diffèrent
entre secteurs : suivre la tendance de chaque secteur dans le temps a plus
de sens que comparer les niveaux absolus entre secteurs.
