# 26 — Charge d'intérêts fédérale en % des recettes de l'État US

## Séries FRED utilisées (données BEA, comptes nationaux NIPA)
- `A091RC1Q027SBEA` : dépenses d'intérêts du gouvernement fédéral,
  trimestriel, milliards de $ (SAAR)
- `FGRECPT` : recettes courantes du gouvernement fédéral, trimestriel,
  milliards de $ (SAAR)

## Choix de source
Ces données existent aussi via l'API FiscalData du Trésor (comptabilité
budgétaire), mais les séries NIPA équivalentes sont **sur FRED** — client
déjà en place, cache déjà géré, une source de panne en moins. La nuance
comptable (NIPA vs budgétaire) ne change pas l'histoire que raconte le
ratio.

## Calcul
```
charge_intérêts (%) = intérêts fédéraux / recettes fédérales × 100
```
Les deux séries sont dans la même unité et la même convention (SAAR) — le
ratio est directement interprétable. Garde-fou de vraisemblance : le chart
échoue explicitement si le ratio sort de [0, 60]% (changement d'unité ou
de définition d'une série).

## Fenêtre : 25 ans (volontairement plus longue que le standard du projet)
L'objet du chart est un changement de **régime** budgétaire : il faut voir
les années 1990-2000 (charge >15%, puis vingt ans de détente portée par la
baisse des taux) pour juger si le niveau actuel est une normalisation ou
une rupture. Sur 10 ans, le chart ne montrerait qu'une hausse sans point de
comparaison.

## Pourquoi ce graphique apporte un vrai plus
C'est la question de **dominance budgétaire** qu'un comité doit suivre
depuis 2023 : quelle part des recettes de l'État part en intérêts avant
toute dépense discrétionnaire ? Plus ce ratio monte :
- plus la politique budgétaire est contrainte (moins de marge
  contracyclique en cas de récession) ;
- plus la tentation politique de tolérer l'inflation ou de peser sur la
  Fed est forte ;
- plus l'offre d'obligations pèse sur le term premium (chart 07) et
  interroge le statut du dollar (chart 20).

À lire en triptyque avec les charts 07 et 20 : le ratio dit la pression,
le term premium dit si le marché commence à la facturer, le dollar dit si
la confiance globale tient.

## Lecture du graphique
- Une seule ligne : la part des recettes absorbée par les intérêts, avec
  percentile 25 ans sur le dernier point
- Bandes grises : récessions NBER (les recettes chutent en récession — le
  ratio peut sauter sans hausse de taux)

## Limitations connues
- Convention NIPA (comptes nationaux) : les montants diffèrent légèrement
  de la comptabilité budgétaire du Trésor (« interest on the public
  debt ») — l'ordre de grandeur et la dynamique sont identiques.
- Le ratio réagit aux deux termes : une chute des recettes (récession,
  baisses d'impôts) le fait monter sans nouvelle dette — croiser avec les
  bandes de récession avant d'interpréter.
- Les intérêts versés par la Fed au Trésor (remises) ne sont pas déduits.
