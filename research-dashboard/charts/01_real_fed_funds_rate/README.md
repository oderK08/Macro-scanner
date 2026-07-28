# 01 — Real Fed Funds Rate (taux directeur réel)

## Séries FRED utilisées
- `FEDFUNDS` : taux des fed funds effectif (nominal, mensuel)
- `PCEPILFE` : Core PCE Price Index (déflateur préféré de la Fed, mensuel)

## Calcul
```
core_pce_yoy = variation annuelle du Core PCE Index (%)
real_rate    = FEDFUNDS - core_pce_yoy
```

## Pourquoi ce graphique apporte un vrai plus
La Fed communique en taux nominal, mais l'impact réel de sa politique
monétaire sur l'économie dépend du taux **réel**. Si l'inflation baisse
plus vite que le taux nominal ne bouge, la politique monétaire devient
mécaniquement plus restrictive — sans que la Fed n'ait besoin de relever
le taux nominal. Ce chart rend ce resserrement "caché" visible.

## Lecture du graphique
- Ligne grise pointillée : taux nominal
- Ligne bleue pleine : taux réel
- Bandes grisées : récessions US (NBER)
- Annotation : percentile du taux réel actuel sur la fenêtre affichée

## Limitations connues
- Le Core PCE est révisé après publication (comme la plupart des séries
  macro). Ce script utilise toujours la valeur la plus récente connue,
  pas la valeur "telle que publiée à l'époque" (vintage/ALFRED).
- La fenêtre affichée est glissante (aujourd'hui - N ans), recalculée à
  chaque run.
