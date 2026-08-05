# 24 — S&P 500 : croissance des cours vs croissance des profits

## Séries / sources
- SEC EDGAR (frames) : `NetIncomeLoss` — le concept le plus universellement
  tagué de tout US-GAAP (toute entreprise publique doit le publier) —
  agrégé sur les constituants actuels du S&P 500, lissé TTM
- FRED : `SP500` — niveau de l'indice

## Calcul
Les deux séries sont **rebasées à 100** au premier trimestre commun de la
fenêtre de 5 ans, puis superposées. Le niveau du S&P 500 est échantillonné
à chaque fin de trimestre des profits (`merge_asof` backward — dernière
clôture connue, jamais une valeur future). L'écart final entre les deux
indices est affiché en bas du graphique : c'est le proxy d'expansion (ou
compression) de multiple sur la fenêtre.

## Pourquoi ce graphique apporte un vrai plus
C'est la version implémentable en données 100% gratuites de la question de
valorisation qu'un comité pose toujours : **la hausse du marché est-elle
payée par les profits ou par l'expansion des multiples ?** Un vrai P/E
agrégé ou une prime de risque actions exigerait les capitalisations
boursières par entreprise (données payantes) ; comparer les croissances
cumulées donne la même information de régime :

- Courbes parallèles = hausse « saine », payée par les profits
- Cours au-dessus des profits = expansion de multiple — le marché paye de
  plus en plus cher chaque dollar de profit ; plus l'écart est grand, plus
  le marché est vulnérable à une déception de résultats ou de taux
- Profits au-dessus des cours = compression — le marché devient moins cher
  en relatif (souvent le terreau des bonnes années suivantes)

À croiser avec le chart 18 : une expansion de multiple avec des taux réels
qui montent est la combinaison la plus fragile.

## Lecture du graphique
- Bleu : indice des cours (base 100)
- Vert : indice des profits TTM (base 100)
- Écart affiché en bas à droite, avec le régime (expansion/compression)

## Limitations connues
- Composition actuelle du S&P 500 appliquée rétroactivement (biais du
  survivant) et agrégat **équipondéré en dollars de profits** — pas pondéré
  par les capitalisations comme l'indice : la comparaison est un proxy de
  régime, pas un P/E rigoureux.
- Le point de départ (base 100) influence l'écart final : la fenêtre
  glissante de 5 ans déplace ce point à chaque édition — comparer le
  régime (signe et tendance de l'écart), pas la valeur absolue d'une
  édition à l'autre.
- Le résultat net agrégé inclut les éléments exceptionnels
  (dépréciations, plus-values) — le TTM en lisse une partie, pas tout.
