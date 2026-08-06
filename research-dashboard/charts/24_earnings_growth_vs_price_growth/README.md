# S&P 500 : croissance des cours vs croissance des profits

## Séries / source
SEC EDGAR (`NetIncomeLoss`, le concept le plus universellement tagué
d'US-GAAP, agrégé sur les constituants actuels du S&P 500, lissé TTM) et
FRED (`SP500`, niveau de l'indice).

## Calcul
Les deux séries sont rebasées à 100 au premier trimestre commun de la
fenêtre de 5 ans. Le niveau de l'indice est échantillonné à chaque fin de
trimestre des profits par `merge_asof` backward (jamais de valeur future).
L'écart final entre les deux indices, affiché sous le graphique, est le
proxy d'expansion ou de compression de multiple.

## Pourquoi ce graphique apporte un vrai plus
C'est la version implémentable en données gratuites de la question de
valorisation qu'un comité pose toujours : la hausse du marché est-elle
payée par les profits ou par l'expansion des multiples ? Des courbes
parallèles signalent une hausse payée par les profits ; des cours qui
s'échappent au-dessus signalent une expansion de multiple, d'autant plus
vulnérable à une déception que l'écart est grand ; des profits au-dessus
des cours signalent une compression, souvent le terreau des bonnes années
suivantes.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement, et agrégat en
dollars de profits non pondéré par les capitalisations : un proxy de
régime, pas un P/E rigoureux. Le point de départ (base 100) se déplace à
chaque édition avec la fenêtre glissante — comparer le régime, pas la
valeur absolue entre éditions. Le résultat net inclut les éléments
exceptionnels, partiellement lissés par le TTM.
