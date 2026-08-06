# Sahm Rule Recession Indicator

## Séries / source
FRED : `UNRATE` (taux de chômage US, mensuel).

## Calcul
Indicateur = moyenne mobile 3 mois du chômage moins son minimum sur les 12
derniers mois. Seuil de déclenchement historique : 0.5 point.

## Pourquoi ce graphique apporte un vrai plus
Un franchissement de 0.5 point a précédé (ou coïncidé très tôt avec) chaque
récession US depuis 1970. Contrairement à « le chômage augmente », signal
lent et bruité, la Sahm Rule capture l'accélération relative du chômage par
rapport à son creux récent — bien plus rapide et fiable en temps réel.

## Limitations connues
FRED publie une version officielle déjà calculée (`SAHMREALTIME`) qui gère
les données vintage ; ce script recalcule à partir de `UNRATE` en valeurs
les plus récentes connues, ce qui peut différer marginalement de la version
officielle.
