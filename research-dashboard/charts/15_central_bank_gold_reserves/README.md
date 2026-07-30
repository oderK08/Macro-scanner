# 15 — Réserves d'or des banques centrales, par pays

## ⚠️ Statut : source non testée en conditions réelles
Contrairement aux autres graphiques du projet (FRED, SEC EDGAR), ce
graphique utilise **DBnomics**, une source dont le domaine
(`api.db.nomics.world`) n'était pas accessible depuis l'environnement de
développement au moment de l'écriture de ce script. La logique est
construite sur la documentation officielle et des exemples confirmés, mais
il est possible que le premier run réel échoue et nécessite un ajustement
-- exactement comme ça a déjà été le cas pour d'autres sources du projet
(ex: `ACMTP10` remplacé par `THREEFYTP10` pour le chart 07). Si ce
graphique échoue, le message d'erreur inclut un extrait de la réponse
brute de l'API pour faciliter le diagnostic.

## Source
[DBnomics](https://db.nomics.world), qui republie en JSON simple les
statistiques du FMI (base **IMF/IFS** -- International Financial
Statistics), incluant les réserves d'or officielles déclarées par pays.

## Pourquoi DBnomics plutôt que l'API du FMI en direct
L'API officielle du FMI utilise le format **SDMX**, plus lourd et
technique (construction de requête en plusieurs étapes, identifiants pays
propres au FMI qui ne suivent pas le format ISO standard). DBnomics
republie les mêmes données via une API REST beaucoup plus simple, en JSON,
sans clé API.

## Méthode
Plutôt que de coder en dur des identifiants pays FMI (fragiles et pas au
format ISO -- ex: `"1C_459"` pour un pays donné dans la base IFS), ce
script interroge l'**API de recherche** de DBnomics en texte libre pour
chaque pays suivi, et prend la série mensuelle de réserves d'or (volume en
onces troy) la plus pertinente trouvée. Le volume est ensuite converti en
tonnes (1 once troy = 31,1034768 grammes).

## Pays suivis
Chine, Russie, Inde, Turquie, Pologne, Kazakhstan, République tchèque —
parmi les plus gros acheteurs d'or connus depuis 2022. Liste ajustable
librement dans `generate.py` (`COUNTRIES`).

## Pourquoi ce graphique apporte un vrai plus
Le narratif de "dé-dollarisation" (les banques centrales, notamment
émergentes, qui diversifient leurs réserves hors dollar en accumulant de
l'or) est un des grands sujets macro depuis le gel des réserves de change
russes en 2022 — un événement qui a démontré que même des réserves en
obligations souveraines détenues à l'étranger peuvent être rendues
inaccessibles par des sanctions. Ce graphique permet de suivre
concrètement qui achète, à quel rythme, et si la tendance s'essouffle ou
s'accélère, plutôt que de se fier à des commentaires qualitatifs.

## Lecture du graphique
- Une ligne par pays, en tonnes de réserves d'or

## Limitations connues
- **Risque d'échec au premier run** (voir avertissement en tête de ce README).
- Les données IFS ont un décalage de publication (souvent 2 mois ou plus
  selon les pays ; certains pays comme l'Allemagne ou la France publient en
  fréquence trimestrielle, pas mensuelle).
- La recherche texte libre par pays peut occasionnellement remonter une
  série légèrement différente de celle attendue si le nom du pays ou la
  terminologie de l'indicateur varie -- à vérifier ponctuellement en
  comparant avec les chiffres publiés par le World Gold Council.
- L'or détenu par un pays n'est pas nécessairement stocké physiquement
  dans ce pays (beaucoup de réserves sont gardées à la Banque d'Angleterre
  ou à la Fed de New York) -- ce chart montre la propriété déclarée, pas la
  localisation physique.
