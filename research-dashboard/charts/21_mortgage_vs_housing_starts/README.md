# Taux hypothécaire 30 ans vs mises en chantier de logements

## Séries / source
FRED : `MORTGAGE30US` (taux hypothécaire fixe 30 ans, enquête Freddie Mac,
hebdomadaire) et `HOUST` (mises en chantier, Census Bureau, mensuel, SAAR).
HOUST est préféré aux ventes de logements existants : statistique
officielle du Census publiée sans interruption depuis 1959, là où une série
privée (NAR) peut changer de méthodologie ou disparaître de FRED.
Alignement par `merge_asof` backward — jamais de valeur future.

## Pourquoi ce graphique apporte un vrai plus
L'immobilier résidentiel est le canal de transmission de la politique
monétaire à l'économie réelle : premier secteur à casser quand les taux
montent, premier à repartir quand ils baissent (« housing is the business
cycle », Leamer 2007), et un moteur direct d'emploi et de demande. Le
délai de transmission est l'information utile : des taux qui baissent sans
reprise des chantiers signalent un blocage ailleurs (coûts, foncier, effet
de verrouillage des ménages à taux bas).

## Limitations connues
`HOUST` est volatil au mois le mois (météo, multifamily) : lire la
tendance, pas le dernier point. Le taux Freddie Mac est un taux d'enquête,
différent du taux effectivement obtenu selon le profil d'emprunteur. Depuis
2022, l'effet de verrouillage a partiellement découplé taux courants et
activité.
