# 12 — Ratio inventaires/ventes par secteur

## Source
SEC EDGAR, endpoint `frames`.

## Concepts XBRL utilisés
- **Inventaires** : `InventoryNet` — poste de **bilan** (photo à une date
  donnée), donc concept "instant". ⚠️ Le format de période EDGAR est
  `CY{année}Q{trimestre}I` (avec un "I" final), différent du format pour un
  concept de flux comme les revenus (`CY{année}Q{trimestre}`, sans "I").
  Oublier ce "I" est l'erreur la plus commune avec l'API `frames` — elle
  renvoie simplement une frame vide, sans message d'erreur explicite.
- **Revenus** (fallback) : `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`

## Calcul
Exprimé comme "% du chiffre d'affaires annuel immobilisé en stock".

## Pourquoi ce graphique apporte un vrai plus
Le ratio inventaires/ventes est un précurseur classique des cycles
industriels et retail :
- **En fin de cycle expansionniste**, les entreprises sur-anticipent la
  demande, accumulent du stock qu'elles n'arrivent plus à écouler aussi
  vite → le ratio monte
- **Avant un restockage** (reprise de cycle), le ratio redescend car les
  stocks ont été épuisés et les entreprises recommencent à commander

## Secteurs suivis
Limité à Technologie, Industrie, Énergie, Consommation, Santé — la Finance,
les Télécoms et les Utilities n'ont pas de "stock" au sens classique
(services, infrastructure), donc un ratio inventaires/ventes n'aurait pas
de sens pour eux et polluerait la lecture du graphique.

## Lecture du graphique
- Une ligne par secteur, couleur distincte
- Bandes grisées : récessions US (NBER)
- Une hausse marquée = signal d'alerte fin de cycle pour ce secteur ; une
  baisse marquée = signal de restockage à venir

## Limitations connues
- Même limitation d'échantillon que les charts 09/10/11 : listes statiques
  de grandes capitalisations par secteur, pas la composition officielle
  d'un indice sectoriel.
- Le ratio est pondéré par la taille des entreprises de l'échantillon
  (comme le chart 11), pas une moyenne simple par entreprise.
- Toutes les entreprises ne gèrent pas leurs stocks de la même façon
  (juste-à-temps vs stockage stratégique) — comparer des secteurs très
  différents en niveau absolu a moins de sens que suivre la tendance de
  chaque secteur dans le temps.
