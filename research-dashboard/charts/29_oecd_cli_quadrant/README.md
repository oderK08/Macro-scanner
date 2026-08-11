# Cycle mondial : quadrant des indicateurs avancés OCDE

## Séries / source
DBnomics, qui republie les Composite Leading Indicators de l'OCDE
(ajustés d'amplitude, mensuels, 100 = tendance de long terme) pour les
États-Unis, la zone euro, le Japon, le Royaume-Uni et la Chine. Recherche
des séries par texte libre et datasets candidats multiples : les
identifiants OCDE ont changé lors de la migration de 2023-2024 et peuvent
rechanger.

⚠️ Source non éprouvée en conditions réelles au moment de l'écriture :
premier run à valider, comme toute nouvelle source du projet.

## Calcul
Scatter façon « quadrant PMI » des notes de banque : niveau du CLI en Y,
variation sur 3 mois en X, un point par économie avec une traîne des 6
derniers mois. Haut-droit = au-dessus de la tendance et en accélération ;
bas-droit = sous la tendance mais en amélioration. Garde-fou : un CLI hors
de [70, 130] fait échouer le chart (série mal identifiée).

## Pourquoi ce graphique apporte un vrai plus
Le CLI est construit par l'OCDE précisément pour anticiper les
retournements du cycle de 6 à 9 mois — c'est l'équivalent institutionnel
et gratuit des quadrants de momentum PMI (payants) utilisés par les desks.
Une seule image répond à la première question d'un comité : où en est
chaque grande économie dans le cycle, et dans quel sens tourne-t-elle ?
La rotation anti-horaire du quadrant donne aussi le coup d'après.

## Limitations connues
Le CLI est révisé chaque mois et publié avec un à deux mois de décalage.
L'ajustement d'amplitude lisse les chocs brutaux (2020). La composition
par pays diffère (enquêtes, carnets de commandes, marchés) — comparer les
positions relatives plutôt que les écarts fins entre pays.
