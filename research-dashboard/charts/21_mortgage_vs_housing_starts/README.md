# 21 — Taux hypothécaire 30 ans vs mises en chantier de logements

## Séries FRED utilisées
- `MORTGAGE30US` : taux hypothécaire fixe 30 ans (enquête Freddie Mac),
  hebdomadaire, %
- `HOUST` : mises en chantier de logements (Census Bureau), mensuel, en
  milliers d'unités, rythme annualisé désaisonnalisé (SAAR)

## Pourquoi HOUST et pas les ventes de logements existants (NAR)
Les mises en chantier sont une statistique **officielle du Census Bureau**,
publiée sans interruption depuis 1959. Les ventes de logements existants
sont une donnée **privée** (National Association of Realtors) qui peut
changer de méthodologie ou être retirée de FRED — c'est déjà arrivé à des
séries privées. Critère de robustesse pour un projet qui doit tourner sans
maintenance pendant des années.

## Calcul
Aucune transformation — deux axes Y séparés, alignement par `merge_asof`
(direction backward, tolérance 45 jours : chaque point hebdomadaire du taux
est associé au dernier point mensuel connu des mises en chantier, sans
jamais regarder dans le futur).

## Pourquoi ce graphique apporte un vrai plus
L'immobilier résidentiel est **le** canal de transmission de la politique
monétaire à l'économie réelle : premier secteur à casser quand les taux
montent, premier à repartir quand ils baissent (« housing IS the business
cycle », Leamer 2007). Les mises en chantier sont de plus un moteur direct
d'emploi (construction) et de demande (matériaux, équipements). Ce chart
montre la transmission en action — y compris son délai, qui est
l'information utile : des taux qui baissent sans reprise des chantiers
signalent un blocage ailleurs (coûts de construction, rareté du foncier,
effet de verrouillage des ménages assis sur un taux à 3%).

## Lecture du graphique
- Bleu (échelle gauche) : taux hypothécaire 30 ans
- Vert (échelle droite) : mises en chantier
- Relation **inverse** attendue, avec 6-12 mois de délai

## Limitations connues
- `HOUST` est volatil au mois le mois (météo, multifamily par nature
  erratique) — lire la tendance, pas le dernier point isolé.
- Le taux Freddie Mac est un taux « affiché » d'enquête : le taux
  effectivement obtenu varie selon le profil d'emprunteur et les points
  payés à l'origination.
- Depuis 2022, l'effet de verrouillage (ménages qui gardent leur taux bas)
  a partiellement découplé taux courants et activité — c'est justement
  visible sur ce chart.
