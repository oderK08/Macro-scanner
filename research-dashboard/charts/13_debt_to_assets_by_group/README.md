# 13 — Debt-to-Assets par groupe (Hyperscalers / Neoclouds / Reste du S&P 500)

## Séries / source
SEC EDGAR, endpoint `frames`.

## Concepts XBRL utilisés
- **Assets** : total des actifs (concept standard, quasi universellement tagué)
- **Dette totale** : `DebtCurrent` + `LongTermDebtNoncurrent` — ⚠️ ce sont des
  **composants à additionner** (portion courante + portion long terme de la
  dette), pas des alternatives comme pour le capex/revenus où un seul
  concept "gagne" par entreprise.

## Groupes suivis
- **Hyperscalers** : MSFT, GOOGL, AMZN, META (définition alignée sur la
  terminologie des notes de recherche des banques)
- **Neoclouds** : CRWV, NBIS, IREN, APLD, CORZ, WULF, CIFR — catégorie
  récente (fournisseurs de cloud spécialisés IA/GPU), liste à réviser plus
  fréquemment que les autres du projet (voir limitations)
- **Reste du S&P 500** : tous les constituants du S&P 500 (voir
  `common/sp500_list.py`) à l'exception des hyperscalers

## Calcul
Calculé directement sur les valeurs de fin de trimestre (postes de bilan,
pas de lissage TTM nécessaire ici contrairement aux ratios basés sur des
flux comme le chiffre d'affaires).

## Pourquoi ce graphique apporte un vrai plus
Le narratif "les hyperscalers financent leur boom capex IA par la dette"
mérite d'être confronté aux chiffres. Comparer leur levier (dette/actifs) à
celui des neoclouds — un modèle bien plus capital-intensif et
structurellement plus endetté — et au reste du marché permet de juger si le
risque de levier est concentré chez les neoclouds, généralisé à tout le
secteur IA, ou en réalité plus prudent qu'on ne le pense spécifiquement
chez les hyperscalers (qui financent une bonne partie de leur capex par
free cash-flow propre, contrairement aux neoclouds).

## Limitations connues
- **Neoclouds** : catégorie très récente et en évolution rapide (nouvelles
  entreprises, IPOs, consolidation possible) — cette liste demandera une
  mise à jour manuelle plus fréquente que le reste du projet.
- **Nebius Group (NBIS)** est une société néerlandaise cotée au Nasdaq —
  elle peut déposer des formulaires différents (20-F/6-K) des dépositaires
  domestiques (10-K/10-Q), avec une couverture EDGAR possiblement moins
  complète ou moins régulière que les entreprises américaines du groupe.
- `DebtCurrent + LongTermDebtNoncurrent` est une approximation de la dette
  totale portant intérêt — certains éléments (baux financiers/opérationnels
  capitalisés, instruments hybrides) peuvent ne pas être capturés selon la
  façon dont chaque entreprise tague son bilan.
- Le "Reste du S&P 500" est une moyenne pondérée par la taille des
  entreprises, pas une moyenne simple par entreprise (même nuance que les
  charts 11/12).
