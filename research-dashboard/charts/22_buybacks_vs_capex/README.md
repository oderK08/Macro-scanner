# Rachats d'actions vs Capex agrégés du S&P 500

## Séries / source
SEC EDGAR, endpoint `frames`, agrégation sur les constituants actuels du
S&P 500. Concepts avec fallback — rachats :
`PaymentsForRepurchaseOfCommonStock`, `PaymentsForRepurchaseOfEquity` ;
capex : mêmes concepts que le chart des capex agrégés.

## Calcul
Somme trimestrielle de chaque flux sur le S&P 500, lissée en TTM
(4 trimestres glissants), en milliards de $.

## Pourquoi ce graphique apporte un vrai plus
Rachats et capex sont les deux grands usages concurrents du cash-flow des
entreprises, et leur rapport est un baromètre de régime : capex supérieur
aux rachats signale des opportunités d'investissement (ou une contrainte,
comme le boom IA) ; rachats supérieurs au capex signalent le retour aux
actionnaires — soutien technique aux cours, parfois symptôme d'un manque
d'idées de croissance. Un croisement des deux courbes est un événement de
régime, pas un détail comptable.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement. Rachats bruts,
sans déduire les émissions d'actions (rémunération en actions). Certaines
entreprises taguent leurs rachats hors des concepts suivis : l'agrégat est
un plancher — la tendance et le croisement restent les informations
fiables.
