# Dette nette / EBITDA par secteur (S&P 500, hors Financières)

## Séries / source
SEC EDGAR, endpoint `frames`. Dette : `DebtCurrent` +
`LongTermDebtNoncurrent` (composants à additionner, postes de bilan avec
suffixe de période « I »). Trésorerie avec fallback
(`CashAndCashEquivalentsAtCarryingValue` et variante restricted). EBITDA
reconstruit : `OperatingIncomeLoss` + dotations aux amortissements
(fallback sur trois concepts de D&A), en flux TTM. Secteurs GICS via
`common/sp500_list.py`, Financières exclues (la dette y est la matière
première du métier, le ratio n'y a pas de sens).

## Calcul
Ratio = (dette − trésorerie) de fin de trimestre / EBITDA TTM. Les points à
EBITDA sectoriel négatif ou nul sont exclus.

## Pourquoi ce graphique apporte un vrai plus
Le debt-to-assets mesure le levier bilantiel ; dette nette/EBITDA mesure la
capacité de remboursement — la métrique des agences de notation et des
covenants (repères usuels : moins de 1x très sain, plus de 3x levier
élevé). Par secteur et net de trésorerie, elle révèle où le levier
s'accumule réellement : la tech est souvent en cash net, les utilities
structurellement à 4-5x sans que ce soit alarmant. La trajectoire de chaque
secteur par rapport à sa propre norme est l'information.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement. L'EBITDA
reconstruit n'est pas l'EBITDA « covenant » des contrats de dette. Les
entreprises dont le D&A échappe aux concepts suivis rendent l'EBITDA
sectoriel un plancher (biais conservateur stable). Comparer chaque secteur
à son propre historique, pas les secteurs entre eux.
