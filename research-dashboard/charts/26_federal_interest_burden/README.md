# Charge d'intérêts fédérale en % des recettes de l'État US

## Séries / source
FRED (données BEA, comptes nationaux NIPA) : `A091RC1Q027SBEA` (dépenses
d'intérêts du gouvernement fédéral) et `FGRECPT` (recettes courantes
fédérales), trimestriels, milliards de $ SAAR. Ces données existent aussi
via l'API FiscalData du Trésor, mais les séries NIPA équivalentes sont sur
FRED : client déjà en place, une source de panne en moins.

## Calcul
Ratio = intérêts / recettes × 100, les deux termes étant dans la même
convention. Fenêtre de 25 ans, volontairement plus longue que le standard
du projet : l'objet est un changement de régime budgétaire, illisible sans
les années 1990-2000 en point de comparaison. Garde-fou : échec explicite
si le ratio sort de [0, 60]%.

## Pourquoi ce graphique apporte un vrai plus
C'est la question de dominance budgétaire à suivre depuis 2023 : quelle
part des recettes de l'État part en intérêts avant toute dépense ? Plus ce
ratio monte, plus la politique budgétaire est contrainte, plus la tentation
de tolérer l'inflation ou de peser sur la Fed est forte, et plus l'offre
d'obligations pèse sur le term premium et interroge le statut du dollar.

## Limitations connues
Convention NIPA, légèrement différente de la comptabilité budgétaire du
Trésor (dynamique identique). Le ratio réagit aussi aux recettes : une
récession le fait monter sans hausse de taux. Les remises de la Fed au
Trésor ne sont pas déduites.
