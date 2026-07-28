# 02 — Sahm Rule Recession Indicator

## Série FRED utilisée
- `UNRATE` : taux de chômage US (mensuel)

## Calcul
```
ma3            = moyenne mobile 3 mois du taux de chômage
min12_of_ma3   = minimum de ma3 sur les 12 derniers mois
sahm_indicator = ma3 - min12_of_ma3
```
Seuil de déclenchement historique : **0.5 point**.

## Pourquoi ce graphique apporte un vrai plus
Un seuil de 0.5 point sur cet indicateur a précédé (ou coïncidé très tôt
avec) chaque récession US depuis 1970. Contrairement à "le chômage
augmente", qui est un signal lent et bruité, la Sahm Rule capture
l'accélération relative du chômage par rapport à son creux récent — un
signal beaucoup plus rapide et fiable en temps réel.

## Lecture du graphique
- Ligne bleue : indicateur Sahm
- Ligne rouge pointillée : seuil de déclenchement (0.5)
- Bandes grisées : récessions US (NBER)

## Limitations connues
- FRED fournit une version officielle déjà calculée (`SAHMREALTIME`) qui
  gère certaines subtilités de données vintage (valeurs telles que
  publiées à l'époque). Ce script recalcule à partir de `UNRATE` en
  valeurs les plus récentes connues — suffisant pour un usage perso, mais
  à garder en tête si tu compares avec la version officielle Fed.
