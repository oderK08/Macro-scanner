# 14 — Interest Coverage Ratio par groupe (Hyperscalers / Neoclouds / Reste du S&P 500 hors Financières)

## Séries / source
SEC EDGAR, endpoint `frames`.

## Concepts XBRL utilisés
- **OperatingIncomeLoss** : proxy d'EBIT (déjà utilisé au chart 11)
- **InterestExpense** : charges d'intérêt, concept standard

## Groupes suivis
- **Hyperscalers** : MSFT, GOOGL, AMZN, META
- **Neoclouds** : CRWV, NBIS, IREN, APLD, CORZ, WULF, CIFR (voir chart 13
  pour les limitations de cette catégorie récente)
- **Reste du S&P 500, hors secteur Financières** : pour une banque, les
  intérêts sont le cœur de métier (elle prête et emprunte en permanence) —
  un ratio de couverture d'intérêts n'a pas le même sens que pour une
  entreprise non-financière, l'inclure fausserait la comparaison

## Calcul
Les deux composantes sont lissées en TTM (glissant sur 4 trimestres) pour
la même raison que le chart 11 : éviter le bruit trimestriel/saisonnier.

## Pourquoi ce graphique apporte un vrai plus
Ce ratio mesure combien de fois le résultat opérationnel couvre les charges
d'intérêt — plus il est élevé, plus l'entité peut absorber sa charge de
dette sans mettre en danger sa solvabilité. Comparer hyperscalers, neoclouds
et reste du marché révèle si le boom d'endettement lié à l'IA a un vrai
coussin de sécurité ou navigue à vue : les hyperscalers financent une bonne
partie de leur capex par free cash-flow propre (donc un ratio
structurellement très élevé est attendu), tandis que les neoclouds,
beaucoup plus jeunes et capital-intensifs, ont un profil de risque
nettement différent.

## Lecture du graphique
- Une ligne par groupe
- Ligne pointillée rouge à 1x : en-dessous, le résultat opérationnel ne
  couvre même plus les charges d'intérêt — signal d'alerte sévère

## Limitations connues
- Mêmes limitations que le chart 13 concernant la liste des neoclouds
  (catégorie récente, Nebius potentiellement moins bien couverte).
- `OperatingIncomeLoss` est un proxy d'EBIT, pas un EBIT au sens strict
  (peut inclure/exclure certains éléments selon les conventions comptables
  de chaque entreprise).
- Un groupe où une seule entreprise domine largement (ex: si un neocloud
  pèse disproportionnellement dans le total) peut faire bouger tout le
  ratio du groupe sur la base d'un seul acteur.
