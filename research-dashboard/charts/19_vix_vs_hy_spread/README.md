# 19 — VIX vs spread crédit High Yield

## Séries FRED utilisées
- `VIXCLS` : indice VIX (volatilité implicite S&P 500 à 30 jours), quotidien
- `BAMLH0A0HYM2` : spread High Yield OAS (ICE BofA), quotidien, points de %

## Calcul
Aucune transformation — les deux séries sont affichées sur deux axes Y
séparés, alignées par `merge_asof`. Le percentile historique de chacune est
affiché sur le dernier point : c'est la **comparaison des deux percentiles**
qui fait la lecture du graphique.

## Pourquoi ce graphique apporte un vrai plus
Le VIX mesure le stress pricé par le marché **actions** (via les options),
le spread HY le stress pricé par le marché du **crédit**. En régime normal,
les deux évoluent ensemble — l'information est dans les **divergences** :

- VIX écrasé + spreads qui s'élargissent discrètement = le crédit voit un
  risque que les actions ignorent — configuration pré-correction classique
- Spreads serrés + VIX élevé = stress de volatilité technique
  (positionnement, couvertures, gamma) plutôt que fondamental — souvent un
  bruit, parfois une opportunité

Le chart 03 compare le crédit au **niveau** des actions ; celui-ci compare
les deux **prix du risque** entre eux — deux lectures complémentaires, pas
redondantes.

## Lecture du graphique
- Violet (échelle gauche) : VIX
- Bleu (échelle droite) : spread HY
- `P{n}` sur les derniers points = percentile de chaque série sur la
  fenêtre affichée ; un écart important entre les deux percentiles signale
  une divergence à investiguer

## Limitations connues
- Les deux axes ont des échelles indépendantes : la superposition visuelle
  est indicative, seule la comparaison des percentiles est rigoureuse.
- Le VIX est borné vers le bas (~9-10) mais pas vers le haut : ses pics
  écrasent visuellement le reste de la série.
- Le spread HY reflète aussi la composition sectorielle du gisement HY
  (énergie notamment) : un choc pétrolier peut élargir le spread sans
  stress systémique.
