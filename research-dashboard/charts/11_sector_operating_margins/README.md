# Marges opérationnelles par secteur

## Séries / source
SEC EDGAR, endpoint `frames`. Revenus avec fallback (`Revenues`,
`RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`),
résultat opérationnel (`OperatingIncomeLoss`). Secteurs GICS officiels des
constituants actuels du S&P 500 via `common/sp500_list.py`.

## Calcul
Par secteur et par trimestre, somme des revenus et du résultat
opérationnel, chacune lissée en TTM (4 trimestres glissants) pour effacer
la saisonnalité ; marge = résultat opérationnel TTM / revenus TTM.

## Pourquoi ce graphique apporte un vrai plus
La compression ou l'expansion de marge sectorielle révèle si le pricing
power d'un secteur entier s'érode. Une marge en baisse chez une entreprise
peut lui être spécifique ; si c'est tout un secteur, c'est un vrai signal
macro-sectoriel — une lecture que les chiffres d'une seule entreprise ne
permettent pas.

## Limitations connues
Composition actuelle du S&P 500 appliquée rétroactivement. La marge
sectorielle est pondérée par la taille des entreprises : un secteur peut
être dominé par un ou deux géants. Les exercices fiscaux décalés
introduisent un léger désalignement trimestriel.
