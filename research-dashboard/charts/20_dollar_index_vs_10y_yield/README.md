# Dollar pondéré par les échanges vs taux 10 ans US

## Séries / source
FRED : `DTWEXBGS` (indice dollar large pondéré par les échanges, Fed Board,
base janvier 2006 = 100, quotidien) et `DGS10` (taux nominal 10 ans,
quotidien). DTWEXBGS est préféré au DXY, indice propriétaire sur-pondéré en
euro et absent de FRED — l'indice officiel de la Fed, pondéré par les
échanges réels (Chine et Mexique inclus), est le bon choix pour un projet
sans maintenance.

## Pourquoi ce graphique apporte un vrai plus
Le cycle du dollar est un des grands régimes macro de l'allocation
globale : un dollar fort resserre les conditions financières mondiales
(dette émergente en dollars, matières premières facturées en dollars) et
pèse sur les bénéfices étrangers du S&P 500 (~40% des revenus). Le taux 10
ans est superposé parce que le différentiel de taux est le principal moteur
du dollar : la configuration la plus riche est la divergence — un dollar
qui baisse alors que les taux montent signale un doute sur le statut de
valeur refuge des actifs US.

## Limitations connues
`DTWEXBGS` ne commence qu'en 2006. L'indice pondéré par les échanges bouge
moins vite que le DXY cité par la presse (poids de devises gérées comme le
yuan) : les mouvements paraissent plus amortis.
