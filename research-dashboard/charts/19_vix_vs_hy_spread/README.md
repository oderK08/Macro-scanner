# VIX vs spread crédit High Yield

## Séries / source
FRED : `VIXCLS` (volatilité implicite S&P 500 à 30 jours, quotidien) et
`BAMLH0A0HYM2` (spread High Yield OAS, quotidien). Deux axes Y, percentile
historique de chaque série affiché en légende.

## Pourquoi ce graphique apporte un vrai plus
Le VIX mesure le stress pricé par le marché actions, le spread HY celui du
marché du crédit. En régime normal les deux évoluent ensemble ;
l'information est dans les divergences. Un VIX écrasé avec des spreads qui
s'élargissent discrètement signale que le crédit voit un risque que les
actions ignorent — configuration pré-correction classique. Des spreads
serrés avec un VIX élevé signalent un stress technique de volatilité plutôt
que fondamental. La comparaison des deux percentiles est la lecture
rigoureuse, les échelles des deux axes étant indépendantes.

## Limitations connues
Le VIX est borné vers le bas mais pas vers le haut : ses pics écrasent
visuellement le reste. Le spread HY reflète aussi la composition du
gisement (l'énergie notamment) : un choc pétrolier peut l'élargir sans
stress systémique.
