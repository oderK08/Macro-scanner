# 22 — Rachats d'actions vs Capex agrégés du S&P 500

## Séries / source
SEC EDGAR, endpoint `frames`, même mécanique que les charts 09/11 (fusion
de concepts XBRL avec fallback, résilience réseau, agrégation sur les
constituants actuels du S&P 500 via `common.sp500_list`).

## Concepts XBRL utilisés (avec fallback)
- **Rachats** : `PaymentsForRepurchaseOfCommonStock`,
  `PaymentsForRepurchaseOfEquity`
- **Capex** : `PaymentsToAcquirePropertyPlantAndEquipment`,
  `PaymentsForCapitalImprovements`, `PaymentsToAcquireProductiveAssets`

## Calcul
Somme trimestrielle de chaque flux sur les constituants du S&P 500 trouvés
dans les frames EDGAR, puis lissage TTM (glissant 4 trimestres), converti
en milliards de $.

## Pourquoi ce graphique apporte un vrai plus
Rachats et capex sont les deux grands usages **concurrents** du cash-flow
des entreprises. Leur rapport est un baromètre de régime :

- **Capex > rachats** : les entreprises voient des opportunités
  d'investissement rentables — ou y sont contraintes (boom IA)
- **Rachats > capex** : retour aux actionnaires privilégié — soutien
  technique aux cours (les entreprises ont été le premier acheteur net
  d'actions US sur la décennie 2010), mais parfois symptôme d'un manque
  d'idées de croissance

Le basculement en cours — boom capex IA financé en partie au détriment des
rachats chez certaines méga-caps — est exactement ce que ce chart rend
visible. Pour un comité d'investissement, un croisement des deux courbes
est un événement de régime, pas un détail comptable.

## Lecture du graphique
- Bleu : capex TTM agrégé — à rapprocher du chart 09 (détail par contributeur)
- Rouge : rachats TTM agrégés
- Les niveaux absolus (Md$) sont affichés sur les derniers points

## Limitations connues
- Composition actuelle du S&P 500 appliquée rétroactivement (biais du
  survivant sur 5 ans — même limitation que les charts 09/11/12).
- Les rachats bruts ≠ rachats nets : les émissions d'actions
  (rémunération en actions notamment) ne sont pas déduites.
- Certaines entreprises regroupent leurs rachats dans des concepts XBRL
  non couverts par les deux candidats — l'agrégat est un plancher, pas une
  valeur exacte. La **tendance** et le **croisement** des courbes restent
  les informations fiables.
