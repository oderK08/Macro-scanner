# 27 — Positionnement spéculatif (CFTC COT) : actions, taux, dollar

## ⚠️ Statut : nouvelle source, premier run réel à valider
Comme toute nouvelle source du projet (cf. chart 15/DBnomics à sa
création), l'API CFTC n'a pas pu être testée en conditions réelles depuis
l'environnement de développement. La logique suit la documentation
officielle du Public Reporting Environment ; si le premier run échoue, le
message d'erreur pointe l'élément à vérifier (connectivité, codes de
contrats, schéma de colonnes).

## Source
CFTC **Public Reporting Environment** (`publicreporting.cftc.gov`) — API
Socrata officielle, gratuite, **sans clé** (la CFTC documente qu'un usage
modéré sans token est attendu ; `common/cftc_client.py` applique un rate
limiting de courtoisie + cache incrémental). Dataset : *Legacy — Futures
Only* (`6dca-aqww`), hebdomadaire (arrêté mardi, publié vendredi),
historique depuis 1986.

## Contrats suivis (`common/config.py::COT_CONTRACTS`)
| Contrat | Code CFTC |
|---|---|
| E-mini S&P 500 | `13874A` |
| T-Note 10 ans | `043602` |
| Dollar Index (ICE) | `098662` |

Identification **par code**, jamais par nom : les noms de contrats sont
réécrits par la CFTC au fil des ans, les codes sont stables sur des
décennies.

## Calcul
```
net_pct_oi = (longs non-commerciaux - shorts non-commerciaux) / open interest × 100
```
La normalisation par l'open interest rend les contrats comparables entre
eux **et dans le temps** (l'OI de l'e-mini a été multiplié plusieurs fois
en 20 ans — une position nette en contrats bruts n'est pas comparable
d'une époque à l'autre). Garde-fou : le chart échoue si |net| > 100% de
l'OI (impossible par construction → schéma API modifié).

## Pourquoi ce graphique apporte un vrai plus
Les prix disent ce que le marché **pense**, le COT dit ce qu'il a déjà
**fait**. Un consensus déjà tout positionné n'a plus d'acheteurs
marginaux : les extrêmes de positionnement spéculatif sont des signaux
contrariens classiques, et les retournements violents (short squeeze
Treasuries, débouclage de shorts dollar) partent presque toujours d'un
positionnement extrême. C'est l'angle mort le plus net d'un pack construit
sur les prix : aucun autre graphique du rapport ne dit « qui est déjà dans
le trade ». Les percentiles 10 ans affichés en légende servent exactement
à ça — repérer quand une position nette est historiquement étirée.

## Lecture du graphique
- Au-dessus de zéro : spéculateurs nets acheteurs ; en dessous : nets
  vendeurs
- L'information n'est pas le niveau mais l'**extrême** : percentile >90
  ou <10 = positionnement étiré, vulnérable au retournement
- Un contrat indisponible est ignoré avec avertissement, les autres
  restent tracés

## Limitations connues
- Les « non-commercials » mélangent hedge funds, CTA et petits
  spéculateurs — le rapport désagrégé (TFF) est plus fin mais son
  historique est plus court ; le Legacy est préféré pour la profondeur.
- Publication vendredi pour un arrêté au mardi : ~3 jours de retard sur
  la réalité du positionnement.
- Le % d'OI ne capture pas les positions en options ni le levier hors
  marchés à terme (swaps, ETF).
- Le signal contrarien fonctionne aux extrêmes, pas en tendance : un
  positionnement moyen ne prédit rien.
