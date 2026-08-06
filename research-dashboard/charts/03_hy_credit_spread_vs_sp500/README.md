# HY Credit Spread vs S&P 500

## Séries / source
FRED : `BAMLH0A0HYM2` (spread High Yield OAS, ICE BofA, quotidien) et
`SP500` (niveau de l'indice, quotidien). Deux axes Y séparés, alignement
par `merge_asof`.

## Pourquoi ce graphique apporte un vrai plus
Le marché du crédit réagit souvent au risque de défaut avant que les
actions ne le pricent : le spread HY s'élargit fréquemment un à deux mois
avant une correction actions significative. La superposition rend ces
décalages visibles.

## Limitations connues
Le S&P 500 est affiché en niveau prix, sans dividendes réinvestis —
suffisant pour repérer des divergences de timing, pas pour comparer des
performances.
