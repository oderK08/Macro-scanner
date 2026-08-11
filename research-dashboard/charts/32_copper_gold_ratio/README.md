# La croissance vue par les métaux : ratio cuivre/or vs taux 10 ans

## Séries / source
FRED : `PCOPPUSDM` (prix mondial du cuivre, FMI, $/tonne, mensuel) et
`DGS10` (taux 10 ans US, moyenné par mois). DBnomics : prix mondial de
l'or ($/once, mensuel) depuis la même base FMI (PCPS) que le cuivre —
l'or n'est plus sur FRED (licence LBMA).

⚠️ Source DBnomics non éprouvée en conditions réelles au moment de
l'écriture : premier run à valider, comme toute nouvelle source du projet.

## Calcul
Ratio = prix du cuivre / prix de l'or, superposé au taux 10 ans US sur
l'axe droit. Garde-fous : prix du cuivre hors de [1 000 ; 50 000] $/t, or
hors de [500 ; 20 000] $/oz ou ratio hors de [0.2 ; 20] fait échouer le
chart — attrape notamment un changement d'unité (cuivre parfois coté en
cents/livre).

## Pourquoi ce graphique apporte un vrai plus
Le classique de Gundlach : le cuivre price la croissance industrielle
mondiale, l'or price la peur et les taux réels. Leur ratio est un vote
des matières premières sur la croissance nominale, historiquement très
corrélé au taux 10 ans — quand les deux divergent, l'un des deux marchés
se trompe, et c'est cette divergence qui fait le signal. Aucun autre
chart du rapport ne fait parler les matières premières.

## Limitations connues
Le cuivre est aussi porté par des facteurs d'offre (mines, Chine,
transition électrique) sans lien avec le cycle. L'or répond aux achats
des banques centrales (chart 15) autant qu'à la peur. Prix mensuels
moyens FMI : environ un mois de décalage de publication.
