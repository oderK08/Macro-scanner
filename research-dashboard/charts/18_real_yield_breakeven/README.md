# 18 — Taux réel 10 ans (TIPS) vs anticipations d'inflation (breakeven)

## Séries FRED utilisées
- `DFII10` : rendement réel du Trésor US 10 ans (TIPS), quotidien, %
- `T10YIE` : breakeven d'inflation 10 ans (nominal − TIPS), quotidien, %

## Calcul
Aucune transformation — les deux composantes du taux nominal 10 ans sont
affichées côte à côte :
```
taux nominal 10 ans ≈ taux réel (DFII10) + anticipations d'inflation (T10YIE)
```
Deux repères horizontaux : zéro (taux réel négatif = répression
financière) et 2% (objectif d'inflation de la Fed, référence naturelle du
breakeven).

## Pourquoi ce graphique apporte un vrai plus
Quand le 10 ans nominal monte, la question qui compte pour l'allocation est
**pourquoi**. Une hausse tirée par le **taux réel** comprime les
valorisations actions — surtout les actifs de duration longue (tech,
growth) — et durcit réellement les conditions financières : c'est le taux
d'actualisation de tous les actifs risqués. Une hausse tirée par le
**breakeven** est un signal opposé : la crédibilité anti-inflation de la
Fed s'érode, les actifs réels et matières premières en profitent. Même
mouvement du nominal, implications d'allocation inverses — ce chart sépare
les deux composantes qu'un simple graphique du 10 ans confond.

## Lecture du graphique
- Bleu : taux réel — le vrai « coût du capital » de l'économie
- Orange : anticipations d'inflation à 10 ans — à comparer au pointillé 2%
- Breakeven ancré ≈ 2-2.5% + taux réel qui bouge = marché qui reprice la
  croissance/l'offre d'obligations, pas l'inflation

## Limitations connues
- Le breakeven n'est pas une anticipation « pure » : il inclut une prime de
  risque d'inflation et une prime de liquidité TIPS (le marché TIPS est
  moins liquide que le nominal, notamment en période de stress — en mars
  2020 le breakeven s'est effondré en partie pour des raisons de liquidité,
  pas d'anticipations).
- Décomposition marché ≠ décomposition modèle : le chart 07 (term premium)
  décompose le même taux nominal selon un axe différent
  (anticipations de taux courts + prime de terme).
