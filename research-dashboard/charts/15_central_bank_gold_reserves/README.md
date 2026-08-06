# Réserves d'or des banques centrales, par pays

## Séries / source
DBnomics (api.db.nomics.world), qui republie en JSON simple les
statistiques du FMI (base IMF/IFS), dont les réserves d'or officielles par
pays. Préféré à l'API SDMX du FMI, plus lourde et aux identifiants pays non
standard. Les séries sont trouvées via l'API de recherche de DBnomics puis
converties d'onces troy en tonnes. Pays suivis dans `COUNTRIES`
(`generate.py`) : les plus gros acheteurs connus depuis 2022.

⚠️ Source non éprouvée en conditions réelles au moment de l'écriture (le
domaine était inaccessible depuis l'environnement de développement) : le
premier run peut nécessiter un ajustement ; en cas d'échec, le message
d'erreur inclut un extrait de la réponse brute de l'API.

## Pourquoi ce graphique apporte un vrai plus
Le narratif de dé-dollarisation (banques centrales émergentes diversifiant
leurs réserves vers l'or depuis le gel des réserves russes en 2022) est un
grand sujet macro. Ce chart montre concrètement qui achète, à quel rythme,
et si la tendance s'accélère ou s'essouffle — plutôt que de s'en remettre à
des commentaires qualitatifs.

## Limitations connues
Décalage de publication des données IFS (souvent deux mois ou plus, et
fréquence trimestrielle pour certains pays). La recherche en texte libre
peut occasionnellement remonter une série imprévue : vérifier ponctuellement
contre le World Gold Council. L'or déclaré n'est pas forcément stocké dans
le pays (propriété, pas localisation).
