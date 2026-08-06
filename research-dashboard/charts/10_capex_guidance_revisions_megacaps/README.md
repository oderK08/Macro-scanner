# Accélération du capex des méga-caps (proxy de révision)

## Séries / source
SEC EDGAR, endpoint `frames`, même mécanique que le chart des capex
agrégés. Tickers suivis : `common.config.MEGACAP_CAPEX_TICKERS` (MSFT,
META, GOOGL, AMZN, AAPL).

## Calcul
Pour chaque méga-cap, capex annualisé (TTM) trimestre après trimestre, puis
variation de ce TTM d'un trimestre à l'autre. Le plan initial (extraire la
guidance textuelle des 10-Q par regex/NLP) a été abandonné : formulations
changeantes, aucune garantie de fiabilité dans la durée. Ce proxy repose
uniquement sur du réalisé, structuré et fiable.

## Pourquoi ce graphique apporte un vrai plus
Une vraie révision de consensus exigerait des données payantes (FactSet,
Bloomberg). Ce proxy capture l'essentiel : le rythme de dépense d'une
méga-cap s'accélère-t-il ou ralentit-il par rapport à sa propre trajectoire
récente ? C'est le signal que cherchent les commentaires de résultats
trimestriels.

## Limitations connues
Proxy réalisé, pas une révision de consensus. Le TTM lisse mais retarde :
une accélération d'un seul trimestre met plusieurs trimestres à se refléter
pleinement.
