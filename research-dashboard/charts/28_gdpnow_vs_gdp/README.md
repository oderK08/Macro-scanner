# 28 — Croissance US en temps réel : nowcast GDPNow vs PIB réalisé

## Séries FRED utilisées
- `GDPNOW` : nowcast GDPNow de la Fed d'Atlanta, % annualisé — estimation
  de la croissance du **trimestre en cours**, mise à jour plusieurs fois
  par mois au fil des publications macro ; pour les trimestres passés,
  dernière estimation avant la publication officielle
- `A191RL1Q225SBEA` : croissance du PIB réel réalisée (BEA), trimestriel,
  % annualisé (QoQ SAAR)

## Calcul
Aucune transformation. Les deux séries sont tracées **indépendamment, sans
merge** : le nowcast a par construction un point de plus que le réalisé —
le trimestre en cours, dont le chiffre officiel n'existe pas encore — et
c'est précisément ce point qui fait la valeur du chart (un merge le ferait
disparaître).

## Pourquoi ce graphique apporte un vrai plus
Tous les autres graphiques du rapport sont rétrospectifs. GDPNow répond à
la question par laquelle une séance de comité **commence** : où en est la
croissance *maintenant* ? Le modèle de la Fed d'Atlanta agrège chaque
publication (consommation, capex, commerce extérieur, stocks…) en une
estimation du trimestre en cours, disponible ~un trimestre avant le
chiffre BEA. Le dernier point bleu est la seule donnée du rapport qui
parle du présent.

La superposition avec le réalisé (barres grises) montre en plus la
**fiabilité historique** du nowcast : bonne en régime normal, prise en
défaut dans les retournements violents (2020) — et cet écart est une
information en soi sur la confiance à accorder au point courant.

## Lecture du graphique
- Barres grises : le fait accompli (PIB réalisé, BEA)
- Ligne bleue : le nowcast — son dernier point (marqué) est l'estimation
  du trimestre en cours
- Écart ligne/barre sur un trimestre passé = erreur du nowcast ce
  trimestre-là

## Limitations connues
- La série FRED `GDPNOW` ne conserve, pour les trimestres passés, que la
  **dernière** estimation avant publication — pas la trajectoire
  intra-trimestre du nowcast (qui peut beaucoup bouger entre début et fin
  de trimestre). Le point courant peut donc encore être révisé.
- GDPNow est un modèle purement mécanique (pas de jugement) : il encaisse
  mal les ruptures brutales (grèves, chocs météo, 2020).
- Le PIB réalisé est lui-même révisé (advance → second → third estimate,
  puis révisions annuelles) — la série reflète la dernière révision connue,
  conformément à la convention du projet (voir README racine).
