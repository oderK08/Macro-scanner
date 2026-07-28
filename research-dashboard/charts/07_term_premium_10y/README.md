# 07 — Term Premium 10 ans (modèle Kim-Wright, Fed Board)

## Séries FRED utilisées
- `THREEFYTP10` : term premium à 10 ans, modèle Kim-Wright (Federal Reserve
  Board), quotidien
- `DGS10` : taux nominal du Trésor US à 10 ans, quotidien

## ⚠️ Changement important par rapport à la version initiale
La première version de ce chart visait la série `ACMTP10` (modèle ACM de la
NY Fed), qui est le modèle le plus cité dans la littérature académique et
les notes de recherche des banques d'investissement. **Cette série n'existe
pas sur FRED** — le modèle ACM n'est publié que directement sur le site de
la NY Fed (fichier Excel téléchargeable), jamais repris par FRED. C'est ce
qui faisait échouer ce graphique silencieusement.

FRED propose une alternative comparable mais distincte : `THREEFYTP10`, le
modèle **Kim-Wright** du Federal Reserve Board. Les deux modèles mesurent le
même concept (la prime de risque sur le 10 ans) avec des méthodologies
différentes ; ils sont fortement corrélés (~0.86 sur les 35 dernières
années) mais pas identiques point par point.

## Calcul
Aucune transformation — les deux séries sont affichées directement.

## Pourquoi ce graphique apporte un vrai plus
Le rendement à 10 ans se décompose en deux éléments : (1) la moyenne des
taux courts anticipés sur les 10 prochaines années, et (2) une prime de
risque (term premium) que les investisseurs exigent pour détenir une
obligation longue plutôt que de rouler des obligations courtes. Une hausse
du taux 10 ans tirée par la prime de risque (aversion au risque,
incertitude budgétaire, offre de dette) ne raconte pas la même histoire
économique qu'une hausse tirée par les anticipations de croissance ou
d'inflation.

## Lecture du graphique
- Ligne grise pointillée : taux nominal 10 ans (DGS10)
- Ligne bleue pleine : term premium (THREEFYTP10, modèle Kim-Wright)
- Point + annotation : dernière valeur du term premium et son percentile
  sur la fenêtre affichée
- Bandes grisées : récessions US (NBER)

## Limitations connues
- Ce n'est pas le modèle ACM (le plus cité dans les notes de recherche des
  banques d'investissement), mais le modèle Kim-Wright — comparable, pas
  identique. Si tu veux spécifiquement le modèle ACM, il faudrait aller le
  chercher directement sur le site de la NY Fed (hors EDGAR/FRED, donc hors
  scope actuel du projet).
- Le term premium est une estimation économétrique, pas une donnée
  observée directement — elle peut être révisée si le modèle est recalibré.
- Le term premium peut être négatif (ce qui a été le cas une bonne partie
  de la décennie 2010) : ce n'est pas une anomalie, juste une conséquence
  du contexte de taux bas et d'assouplissement quantitatif.
