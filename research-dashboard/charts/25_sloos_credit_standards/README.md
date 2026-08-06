# Conditions de crédit bancaire (SLOOS) vs spread High Yield

## Séries / source
FRED : `DRTSCILM` (enquête SLOOS de la Fed — % net de banques domestiques
durcissant leurs standards de prêt C&I aux grandes et moyennes entreprises,
trimestriel) et `BAMLH0A0HYM2` (spread High Yield OAS, quotidien). Le
spread est raccroché à chaque date d'enquête par `merge_asof` backward.

## Pourquoi ce graphique apporte un vrai plus
Le SLOOS mesure le robinet du crédit à la source — ce que les banques font,
pas ce que le marché price. Un pic de durcissement précède historiquement
la montée des défauts et la récession de trois à quatre trimestres. La
superposition avec le spread HY répond à la question qui compte : le marché
price-t-il déjà ce que les banques font ? Un SLOOS qui se durcit avec des
spreads encore serrés est la divergence la plus dangereuse ; un SLOOS qui
s'assouplit avec des spreads larges a historiquement été un bon point
d'entrée sur le crédit.

## Limitations connues
Enquête trimestrielle publiée avec environ un mois de décalage, quatre
points par an. Le % net ne mesure pas l'intensité du durcissement, et ne
couvre que les banques domestiques — le crédit non bancaire (private
credit, obligataire), devenu majeur, n'y est pas.
