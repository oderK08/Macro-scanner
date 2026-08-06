# Debt-to-Assets par groupe (Hyperscalers / Neoclouds / Reste du S&P 500)

## Séries / source
SEC EDGAR, endpoint `frames`. Actifs : `Assets`. Dette : `DebtCurrent` +
`LongTermDebtNoncurrent` — deux composants à additionner (portion courante
+ portion long terme), pas des alternatives. Groupes : hyperscalers (MSFT,
GOOGL, AMZN, META), neoclouds (CRWV, NBIS, IREN, APLD, CORZ, WULF, CIFR),
reste du S&P 500.

## Calcul
Ratio dette/actifs sur les valeurs de fin de trimestre (postes de bilan,
pas de lissage TTM nécessaire).

## Pourquoi ce graphique apporte un vrai plus
Le narratif « les hyperscalers financent leur boom capex IA par la dette »
mérite d'être confronté aux chiffres : comparer leur levier à celui des
neoclouds (modèle bien plus capital-intensif) et au reste du marché montre
si le risque est concentré, généralisé, ou plus prudent qu'on ne le pense
chez les hyperscalers, qui financent l'essentiel par leur free cash-flow.

## Limitations connues
La liste des neoclouds est une catégorie récente à réviser plus souvent que
le reste du projet ; Nebius (NBIS, société néerlandaise) peut avoir une
couverture EDGAR moins régulière (formulaires 20-F/6-K). La somme des deux
concepts de dette approxime la dette portant intérêt sans capturer tous les
baux et instruments hybrides. Le « Reste du S&P 500 » est pondéré par la
taille des entreprises.
