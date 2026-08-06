# Positionnement spéculatif (CFTC COT) : actions, taux, dollar

## Séries / source
CFTC Public Reporting Environment (`publicreporting.cftc.gov`), API Socrata
officielle, gratuite et sans clé — dataset Legacy Futures Only,
hebdomadaire, historique depuis 1986. Client dédié :
`common/cftc_client.py` (rate limiting de courtoisie, cache incrémental).
Contrats suivis via `common.config.COT_CONTRACTS` : e-mini S&P 500
(`13874A`), T-Note 10 ans (`043602`), Dollar Index ICE (`098662`) —
identifiés par code, jamais par nom, les noms étant réécrits par la CFTC au
fil des ans.

⚠️ Source non éprouvée en conditions réelles au moment de l'écriture :
premier run à valider, comme toute nouvelle source du projet.

## Calcul
Position nette des non-commerciaux (longs moins shorts) rapportée à l'open
interest, en % — la normalisation rend les contrats comparables entre eux
et dans le temps. Garde-fou : une position nette dépassant 100% de l'open
interest est impossible par construction et fait échouer le chart (schéma
d'API modifié).

## Pourquoi ce graphique apporte un vrai plus
Les prix disent ce que le marché pense, le COT dit ce qu'il a déjà fait. Un
consensus déjà tout positionné n'a plus d'acheteurs marginaux : les
extrêmes de positionnement sont des signaux contrariens classiques, et les
retournements violents partent presque toujours d'un positionnement étiré.
Aucun autre graphique du rapport ne dit qui est déjà dans le trade — les
percentiles en légende signalent précisément ces extrêmes.

## Limitations connues
Les non-commerciaux mélangent hedge funds, CTA et petits spéculateurs.
Publication le vendredi pour un arrêté au mardi. Les positions en options
et le levier hors futures ne sont pas capturés. Le signal contrarien vaut
aux extrêmes, pas en tendance.
