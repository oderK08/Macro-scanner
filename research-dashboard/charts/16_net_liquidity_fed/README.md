# 16 — Liquidité nette de la Fed (bilan - RRP - TGA) vs S&P 500

## Séries FRED utilisées
- `WALCL` : total du bilan de la Fed, hebdomadaire, **en millions de $**
- `RRPONTSYD` : encours du Reverse Repo overnight (ON RRP), quotidien, **en milliards de $**
- `WTREGEN` : Treasury General Account (compte du Trésor à la Fed), hebdomadaire, **en millions de $**
- `SP500` : niveau de l'indice S&P 500, quotidien (superposition, échelle droite)

## Calcul
```
liquidité_nette ($T) = WALCL/1e6 - RRPONTSYD/1e3 - WTREGEN/1e6
```
⚠️ Les trois séries ne sont **pas dans la même unité**, et pas de façon
intuitive : WALCL et WTREGEN en millions, RRPONTSYD en milliards. C'est
l'erreur classique sur ce calcul — la première version de ce chart l'a
faite (WTREGEN supposé en milliards → TGA surestimé ×1000 → « liquidité
nette » à -900 trillions). Un garde-fou de vraisemblance dans
`generate()` fait désormais échouer le chart explicitement si le résultat
sort de l'intervalle plausible [0, 20] T$, plutôt que de publier un
graphique absurde dans le rapport.

Alignement temporel par `merge_asof` (tolérance 7 jours) sur la base de
WALCL, qui est hebdomadaire (publié le mercredi).

## Pourquoi ce graphique apporte un vrai plus
Le bilan brut de la Fed ne dit pas combien de liquidité atteint réellement
les marchés : ce qui est parqué au Reverse Repo ou sur le compte du Trésor
(TGA) est **stérilisé** — retiré du système financier. La liquidité nette
(bilan − RRP − TGA) est la mesure que suivent les desks actions ; sa
corrélation avec le S&P 500 depuis 2020 en a fait l'un des indicateurs de
liquidité les plus regardés du marché. Une remontée du TGA (après un
relèvement du plafond de dette, par exemple) ou du RRP draine de la
liquidité même à bilan Fed constant — ce chart rend ces mouvements visibles
là où le bilan seul les masque.

## Lecture du graphique
- Ligne bleue (échelle gauche) : liquidité nette en trillions de $
- Ligne grise pointillée (échelle droite) : S&P 500
- Divergence marquée entre les deux = signal à investiguer (la liquidité
  mène souvent, mais pas toujours)

## Limitations connues
- La corrélation liquidité nette / S&P 500 est un phénomène surtout
  documenté depuis 2020 (ère du QE massif) — elle était moins nette avant.
  Corrélation n'est pas causalité : les deux peuvent répondre à un
  troisième facteur.
- `RRPONTSYD` est quotidien mais aligné sur la grille hebdomadaire de
  WALCL : les mouvements intra-semaine du RRP sont lissés.
- La série FRED `SP500` ne couvre que ~10 ans glissants — la superposition
  S&P 500 peut démarrer après le début de la fenêtre de liquidité.
