# Capex par principaux contributeurs + tendance annuelle

## Séries / source
SEC EDGAR, endpoint `frames`. Concepts XBRL avec fallback :
`PaymentsToAcquirePropertyPlantAndEquipment`, `PaymentsForCapitalImprovements`,
`PaymentsToAcquireProductiveAssets`. Constituants actuels du S&P 500 via
`common/sp500_list.py`.

## Calcul
Fenêtre courte (3 ans) en détail trimestriel : les 6 plus gros
contributeurs sont montrés individuellement (barres empilées), le reste
regroupé en « Autres ». Une tendance annuelle glissante (TTM) est
superposée sur l'axe secondaire pour lisser le bruit trimestriel.

## Pourquoi ce graphique apporte un vrai plus
Le capex agrégé total ne dit pas qui pousse la tendance. Avec l'explosion
des dépenses d'infrastructure IA, savoir si la hausse vient de trois ou
quatre hyperscalers concentrés ou d'une base large d'entreprises change
complètement l'interprétation du signal macro.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement (biais du
survivant). Les exercices fiscaux décalés entre entreprises introduisent un
léger désalignement trimestriel.
