# Liquidité nette de la Fed (bilan - RRP - TGA) vs S&P 500

## Séries / source
FRED : `WALCL` (bilan de la Fed, hebdomadaire, en millions de $),
`RRPONTSYD` (Reverse Repo overnight, quotidien, en milliards de $),
`WTREGEN` (Treasury General Account, hebdomadaire, en millions de $) et
`SP500` (superposition, échelle droite).

## Calcul
Liquidité nette ($T) = WALCL/1e6 − RRPONTSYD/1e3 − WTREGEN/1e6. Les unités
FRED ne sont pas homogènes, et pas de façon intuitive — la première version
de ce chart supposait WTREGEN en milliards, surestimant le TGA d'un facteur
1000. Un garde-fou fait désormais échouer le chart explicitement si le
résultat sort de l'intervalle plausible [0, 20] T$.

## Pourquoi ce graphique apporte un vrai plus
Le bilan brut de la Fed ne dit pas combien de liquidité atteint les
marchés : ce qui est parqué au Reverse Repo ou sur le compte du Trésor est
stérilisé. La liquidité nette est la mesure suivie par les desks actions,
dont la corrélation avec le S&P 500 depuis 2020 en a fait un des
indicateurs les plus regardés — une remontée du TGA ou du RRP draine la
liquidité même à bilan constant.

## Limitations connues
La corrélation avec le S&P 500 est surtout documentée depuis 2020 et n'est
pas causale. Le RRP quotidien est aligné sur la grille hebdomadaire de
WALCL, lissant les mouvements intra-semaine. La série FRED `SP500` ne
couvre que ~10 ans glissants.
