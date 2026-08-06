# 25 — Conditions de crédit bancaire (SLOOS) vs spread High Yield

## Séries FRED utilisées
- `DRTSCILM` : Senior Loan Officer Opinion Survey (Fed) — % net de banques
  domestiques **durcissant** leurs standards de prêt C&I aux
  grandes/moyennes entreprises, trimestriel
- `BAMLH0A0HYM2` : spread High Yield OAS (ICE BofA), quotidien

## Calcul
Aucune transformation. Le spread HY (quotidien) est raccroché à chaque date
d'enquête SLOOS (trimestrielle) par `merge_asof` backward — dernière valeur
connue à la date de l'enquête, jamais une valeur future.

## Pourquoi ce graphique apporte un vrai plus
Le SLOOS mesure le robinet du crédit **à la source** — ce que les banques
font, pas ce que le marché price. Historiquement, un pic de durcissement
précède la montée des défauts et la récession de **3 à 4 trimestres** :
c'est l'un des indicateurs avancés de cycle de crédit les plus fiables, et
l'enquête que tout comité de crédit lit chaque trimestre.

La superposition avec le spread HY répond à la question qui compte : le
marché price-t-il déjà ce que les banques font ?
- **SLOOS qui se durcit + spreads serrés** = la divergence la plus
  dangereuse — le coût du risque monte à la source mais n'est pas encore
  payé par les investisseurs (configuration pré-2008, pré-2023)
- **SLOOS qui s'assouplit + spreads larges** = le crédit bancaire rouvre
  avant le marché — historiquement un bon point d'entrée sur le crédit

Complète les charts 03 (crédit vs actions) et 06 (conditions financières
composites) : le NFCI agrège une centaine de séries de marché, le SLOOS est
la seule mesure directe du comportement des prêteurs.

## Lecture du graphique
- Bleu (échelle gauche) : % net de banques durcissant — au-dessus de la
  ligne zéro, le crédit se resserre
- Rouge pointillé (échelle droite) : spread HY
- Les bandes grises sont les récessions NBER : noter que le SLOOS pique
  systématiquement avant ou au tout début de chaque bande

## Limitations connues
- Enquête trimestrielle publiée avec ~1 mois de décalage — 4 points par an
  seulement, la ligne est anguleuse par nature.
- Le % net ne dit pas l'**intensité** du durcissement (une banque qui
  durcit « un peu » et une qui coupe tout comptent pareil).
- Couvre les prêts C&I des banques domestiques — le crédit non bancaire
  (private credit, obligataire), devenu majeur, n'y est pas.
