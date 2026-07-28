# 09 — Capex par principaux contributeurs (3 dernières années) + tendance annuelle

## Source
SEC EDGAR, endpoint `frames` — récupère un concept XBRL donné pour **toutes**
les entreprises qui le publient, sur un trimestre donné, en un seul appel
API.

## Concepts XBRL utilisés (avec fallback)
1. `PaymentsToAcquirePropertyPlantAndEquipment`
2. `PaymentsForCapitalImprovements`
3. `PaymentsToAcquireProductiveAssets`

## Ce qui a changé par rapport à la première version
La première version montrait le capex agrégé total sur 10 ans, une seule
ligne. Sur demande, ce chart se concentre maintenant sur :
- **Les 3 dernières années seulement**, en détail trimestriel (plus lisible
  qu'une décennie complète quand on décompose par entreprise)
- **Une décomposition par principal contributeur** : les 6 entreprises qui
  pèsent le plus dans le total sur la fenêtre affichée sont montrées
  individuellement (barres empilées), le reste est regroupé en "Autres"
- **Une tendance annuelle superposée** : somme glissante sur 12 mois (TTM,
  "trailing twelve months"), qui lisse le bruit trimestriel et montre la
  dynamique annuelle sous-jacente, sur un axe Y secondaire

## Calcul
1. Pour chaque trimestre des `DISPLAY_YEARS + 1` dernières années (l'année
   en plus sert uniquement à calculer le TTM dès le premier trimestre
   affiché) : appel `frames`, filtrage sur `SP500_LARGE_CAP_SAMPLE`
2. Table pivot (date x entreprise), les 6 plus gros contributeurs sur la
   fenêtre affichée sont isolés, le reste est sommé dans "Autres"
3. TTM = somme glissante sur 4 trimestres du total agrégé

## Pourquoi ce graphique apporte un vrai plus
Le capex agrégé total (version précédente) ne dit pas **qui** pousse la
tendance. Avec l'explosion des dépenses d'infrastructure IA, savoir si la
hausse vient de 3-4 hyperscalers concentrés ou d'une base large
d'entreprises change complètement l'interprétation du signal macro — un
capex qui explose parce que 3 entreprises misent massivement sur l'IA n'a
pas la même signification qu'un capex qui monte parce que l'ensemble de
l'économie réinvestit.

## Lecture du graphique
- Barres empilées (axe gauche) : capex trimestriel par entreprise
  (6 principaux contributeurs + "Autres")
- Ligne noire avec marqueurs (axe droit) : tendance annuelle glissante (TTM)
- Annotations : total du dernier trimestre affiché, et dernière valeur TTM

## ⚠️ Limitation majeure — à bien
