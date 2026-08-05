# 20 — Dollar pondéré par les échanges vs taux 10 ans US

## Séries FRED utilisées
- `DTWEXBGS` : indice dollar large pondéré par les échanges (Fed Board,
  base janvier 2006 = 100), quotidien
- `DGS10` : rendement nominal du Trésor US 10 ans, quotidien, %

## Pourquoi DTWEXBGS et pas le DXY
Le DXY (ICE) est un indice propriétaire sur-pondéré en euro (~58%) et
**non disponible sur FRED**. `DTWEXBGS` est l'indice officiel de la Fed,
pondéré par les échanges commerciaux réels (Chine et Mexique inclus),
publié par une source publique stable — le bon choix pour un projet qui
doit tourner sans maintenance pendant des années.

## Calcul
Aucune transformation — les deux séries sont affichées sur deux axes Y
séparés, alignées par `merge_asof`.

## Pourquoi ce graphique apporte un vrai plus
Le cycle du dollar est l'un des grands régimes macro pour l'allocation
globale. Un dollar fort resserre les conditions financières **mondiales**
(dette émergente libellée en dollars, matières premières facturées en
dollars) et pèse mécaniquement sur les bénéfices étrangers des
multinationales US (~40% des revenus du S&P 500 viennent de l'étranger).
Le taux 10 ans est superposé parce que le différentiel de taux est le
principal moteur du dollar : la configuration la plus riche d'information
est la **divergence** — un dollar qui baisse alors que les taux montent
signale que le marché doute du statut de valeur refuge des actifs US
(configuration observée en 2025 autour des tensions commerciales et
budgétaires).

## Lecture du graphique
- Bleu (échelle gauche) : indice dollar — percentile 10 ans affiché sur le
  dernier point
- Gris pointillé (échelle droite) : taux 10 ans
- Corrélation positive attendue ; divergence = signal

## Limitations connues
- `DTWEXBGS` ne commence qu'en 2006 (non bloquant pour une fenêtre de 10
  ans glissants, à garder en tête si `HISTORY_YEARS` était un jour rallongé).
- L'indice pondéré par les échanges bouge moins vite que le DXY (poids de
  devises gérées comme le yuan) : les mouvements paraissent plus amortis
  que ce que raconte la presse financière, qui cite presque toujours le DXY.
