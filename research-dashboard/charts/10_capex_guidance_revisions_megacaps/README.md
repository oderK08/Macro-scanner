# 10 — Accélération du capex des méga-caps (proxy de révision)

## Séries / source
SEC EDGAR, endpoint `frames`, même mécanique que le chart 09 (fusion des
concepts XBRL, résilience réseau). Tickers suivis :
`common.config.MEGACAP_CAPEX_TICKERS` (MSFT, META, GOOGL, AMZN, AAPL par
défaut).

## ⚠️ Changement de méthode par rapport au plan initial
Le plan initial de ce projet (voir les toutes premières discussions)
prévoyait d'extraire la **guidance textuelle** ("nous prévoyons désormais un
capex de X Md$ pour l'année") directement depuis le texte libre du MD&A des
10-Q ou des communiqués de résultats, via regex/NLP.

**Cette approche a été abandonnée** avant implémentation, pour deux raisons :
1. La formulation de la guidance change à chaque entreprise et à chaque
   trimestre — un extracteur regex fiable dans la durée demanderait une
   maintenance constante et resterait fragile (aucune garantie qu'il
   fonctionne encore l'année prochaine si une entreprise change sa façon de
   formuler sa guidance).
2. EDGAR ne structure pas cette information — ce serait du texte libre, pas
   une donnée XBRL exploitable simplement.

**Ce qui est implémenté à la place** : une "révision implicite", basée sur
des données réalisées (donc fiables et structurées) plutôt que sur du texte.
Pour chaque méga-cap, on calcule le capex annualisé (TTM, glissant sur 12
mois) trimestre après trimestre, puis sa variation d'un trimestre à
l'autre. Une accélération du TTM signale que l'entreprise dépense plus vite
que sa propre tendance récente — corrélé avec (mais pas identique à) une
révision à la hausse de la guidance.

## Calcul
