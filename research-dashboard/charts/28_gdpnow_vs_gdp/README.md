# Croissance US en temps réel : nowcast GDPNow vs PIB réalisé

## Séries / source
FRED : `GDPNOW` (nowcast de la Fed d'Atlanta — estimation de la croissance
annualisée du trimestre en cours, mise à jour au fil des publications
macro) et `A191RL1Q225SBEA` (croissance du PIB réel réalisée, BEA,
trimestriel, annualisée).

## Calcul
Les deux séries sont tracées indépendamment, sans merge : le nowcast a par
construction un point de plus que le réalisé — le trimestre en cours, dont
le chiffre officiel n'existe pas encore — et c'est précisément ce point qui
fait la valeur du chart.

## Pourquoi ce graphique apporte un vrai plus
Tous les autres graphiques du rapport sont rétrospectifs. GDPNow répond à
la question par laquelle une séance de comité commence : où en est la
croissance maintenant ? Le modèle agrège chaque publication macro en une
estimation du trimestre en cours, disponible environ un trimestre avant le
chiffre BEA — le dernier point est la seule donnée du rapport qui parle du
présent. La superposition avec le réalisé montre aussi la fiabilité
historique du nowcast, et cet écart est une information en soi.

## Limitations connues
La série FRED ne conserve, pour les trimestres passés, que la dernière
estimation avant publication — pas la trajectoire intra-trimestre, qui peut
beaucoup bouger. GDPNow est purement mécanique et encaisse mal les ruptures
brutales (2020). Le PIB réalisé est lui-même révisé ; la série reflète la
dernière révision connue, conformément à la convention du projet.
