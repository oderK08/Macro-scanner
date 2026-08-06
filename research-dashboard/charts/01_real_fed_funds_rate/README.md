# Real Fed Funds Rate (taux directeur réel)

## Séries / source
FRED : `FEDFUNDS` (taux des fed funds effectif, mensuel) et `PCEPILFE`
(Core PCE Price Index, le déflateur préféré de la Fed, mensuel).

## Calcul
Taux réel = FEDFUNDS moins la variation annuelle du Core PCE (%).

## Pourquoi ce graphique apporte un vrai plus
La Fed communique en taux nominal, mais l'impact réel de sa politique
monétaire dépend du taux réel. Si l'inflation baisse plus vite que le taux
nominal ne bouge, la politique devient mécaniquement plus restrictive sans
que la Fed n'ait rien relevé — ce chart rend ce resserrement caché visible.

## Limitations connues
Le Core PCE est révisé après publication ; le script utilise toujours la
valeur la plus récente connue, pas la valeur telle que publiée à l'époque
(vintage/ALFRED).
