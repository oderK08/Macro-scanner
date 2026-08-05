# 23 — Dette nette / EBITDA par secteur (S&P 500, hors Financières)

## Séries / source
SEC EDGAR, endpoint `frames`.

## Concepts XBRL utilisés
- **Dette** (composants **à additionner**, comme chart 13) : `DebtCurrent`
  + `LongTermDebtNoncurrent` — postes de bilan (« instant », période `CY..QI`)
- **Trésorerie** (fallback) : `CashAndCashEquivalentsAtCarryingValue`,
  `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` — bilan aussi
- **EBITDA reconstruit** (flux, période `CY..Q` sans « I ») :
  `OperatingIncomeLoss` + D&A (fallback :
  `DepreciationDepletionAndAmortization`,
  `DepreciationAmortizationAndAccretionNet`, `DepreciationAndAmortization`)

⚠️ Ce chart mélange concepts « instant » et « duration » pour un même
trimestre, comme le chart 12 — le suffixe « I » du format de période EDGAR
ne s'applique qu'aux postes de bilan.

## Calcul
Par secteur GICS et par trimestre :
```
dette_nette = somme(dette) - somme(trésorerie)            [photo fin de trimestre]
EBITDA_TTM  = TTM(somme(résultat op.)) + TTM(somme(D&A))  [flux lissé 4 trimestres]
ratio       = dette_nette / EBITDA_TTM
```
Le secteur **Financières est exclu** : pour une banque la dette est la
matière première du métier, pas un levier — le ratio n'y a aucun sens.
Les points où l'EBITDA TTM sectoriel est négatif ou nul sont exclus
(ratio sans signification).

## Pourquoi ce graphique apporte un vrai plus
Le debt-to-assets (chart 13) mesure le levier **bilantiel** ; dette
nette/EBITDA mesure la **capacité de remboursement** — c'est LA métrique
des agences de notation et des covenants bancaires (repères usuels : <1x
très sain, >3x levier élevé, >4x zone spéculative). Par secteur, elle
révèle où le levier s'accumule réellement, **en tenant compte de la
trésorerie** : la tech est très endettée en brut mais souvent en cash net
(ratio négatif), les utilities structurellement à 4-5x sans que ce soit
alarmant (cash-flows régulés). C'est la trajectoire de chaque secteur par
rapport à sa propre norme qui est l'information.

## Lecture du graphique
- Une ligne par secteur GICS (hors Financières)
- Pointillé rouge à 3x : seuil usuel de levier élevé
- Tirets à 0x : en-dessous, le secteur est en **cash net** (plus de
  trésorerie que de dette)

## Limitations connues
- Composition actuelle du S&P 500 appliquée rétroactivement (biais du
  survivant, comme charts 09/11/12).
- L'EBITDA reconstruit (résultat op. + D&A) est un proxy — il ne
  correspond pas exactement à l'EBITDA « covenant » négocié dans les
  contrats de dette (qui inclut de nombreux ajustements).
- Les entreprises qui taguent leur D&A dans un concept non couvert par les
  trois candidats contribuent au résultat opérationnel mais pas au D&A du
  secteur : l'EBITDA sectoriel est un plancher, donc le ratio un plafond —
  biais conservateur, stable dans le temps.
- Utilities et Real Estate portent structurellement des ratios élevés :
  comparer chaque secteur à son propre historique, pas les secteurs entre eux.
