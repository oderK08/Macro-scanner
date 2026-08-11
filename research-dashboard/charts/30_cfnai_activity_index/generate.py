"""
Graphique : Chicago Fed National Activity Index (CFNAI) -- momentum de
l'activité US résumé en un chiffre.

Série FRED :
  - CFNAI : indice composite de 85 indicateurs mensuels d'activité US
            (production, emploi, consommation, ventes), pondérés par la Fed
            de Chicago. 0 = croissance au rythme tendanciel, positif =
            au-dessus de la tendance, négatif = en-dessous.

La moyenne mobile 3 mois (CFNAI-MA3, calculée ici depuis la série brute --
une série de moins à télécharger, résultat identique) est LA lecture
standard : sous -0.70 après une expansion, elle a historiquement signalé
l'entrée en récession ; au-dessus de +0.70 après une reprise, une surchauffe.

Pourquoi c'est utile : c'est l'équivalent gratuit et méthodologiquement
sérieux d'un "score de momentum macro" propriétaire -- 85 indicateurs
agrégés par une Fed régionale en un seul chiffre comparable sur 50 ans.
Le comité y lit d'un coup d'œil si l'économie US accélère ou décélère par
rapport à sa tendance, sans dépendre d'une enquête unique.

Sortie : PNG dans output/{periode}/30_cfnai_activity_index.png
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.fred_client import get_series
from common.chart_style import (
    setup_figure, add_recession_bands, add_source_footer, format_date_axis,
    add_freshness_subtitle, mark_last_point, format_last_value_label,
    finalize_chart, COLOR_ACCENT, COLOR_SECOND, COLOR_THIRD,
)
from common.config import get_current_period_label, OUTPUT_DIR, HISTORY_YEARS

RECESSION_THRESHOLD = -0.70

# Garde-fou : le CFNAI est un indice standardisé qui vit normalement entre
# -1 et +1 ; avril 2020 a atteint environ -18, le rebond +6. Une valeur
# hors de [-30, 30] ne peut être qu'une série mal identifiée ou un
# changement d'unité -- échec explicite plutôt que graphique absurde.
PLAUSIBLE_RANGE = (-30, 30)


def compute_cfnai(years: int = HISTORY_YEARS) -> pd.DataFrame:
    """
    Retourne un DataFrame: date, cfnai, ma3.
    On télécharge un peu plus d'historique que la fenêtre affichée pour que
    la moyenne mobile 3 mois soit définie dès le premier point affiché.
    """
    raw = get_series("CFNAI", years=years + 1)
    raw = raw.rename(columns={"value": "cfnai"}).sort_values("date").reset_index(drop=True)
    raw["ma3"] = raw["cfnai"].rolling(3).mean()

    date_min = raw["date"].max() - pd.DateOffset(years=years)
    return raw[raw["date"] >= date_min].dropna(subset=["ma3"]).reset_index(drop=True)


def generate():
    df = compute_cfnai()

    if df.empty:
        raise RuntimeError(
            "[30_cfnai_activity_index] Aucune donnée récupérée depuis FRED (CFNAI). "
            "Vérifie FRED_API_KEY et la connectivité réseau."
        )

    lo, hi = PLAUSIBLE_RANGE
    worst = df["cfnai"].abs().max()
    if worst > max(abs(lo), abs(hi)):
        raise RuntimeError(
            f"[30_cfnai_activity_index] Valeur CFNAI implausible ({worst:.1f}, attendu "
            f"dans [{lo}, {hi}]) -- la série FRED a probablement changé de définition."
        )

    fig, ax = setup_figure()
    add_recession_bands(ax, date_min=df["date"].min(), date_max=df["date"].max())

    last_row = df.iloc[-1]

    line_raw, = ax.plot(df["date"], df["cfnai"], color=COLOR_THIRD, linewidth=0.9,
                        alpha=0.8, label="CFNAI mensuel (brut)", zorder=2)
    line_ma3, = ax.plot(df["date"], df["ma3"], color=COLOR_ACCENT, linewidth=1.9,
                        label=format_last_value_label(
                            "CFNAI moyenne 3 mois", f"{last_row['ma3']:+.2f}",
                            series=df["ma3"], years_label=f"{HISTORY_YEARS} ans"),
                        zorder=3)
    line_thr = ax.axhline(RECESSION_THRESHOLD, color=COLOR_SECOND, linewidth=1.2,
                          linestyle="--", zorder=2,
                          label=f"Seuil récession historique ({RECESSION_THRESHOLD:+.2f})")
    ax.axhline(0, color="#999999", linewidth=0.8, zorder=1)

    mark_last_point(ax, last_row["date"], last_row["ma3"])

    format_date_axis(ax, tight_to_last_point=last_row["date"])
    ax.set_ylabel("Indice (0 = croissance tendancielle)", fontsize=9)
    ax.set_title("Momentum de l'activité US : Chicago Fed National Activity Index",
                 fontsize=13, fontweight="bold", color="#222222", loc="left")
    add_freshness_subtitle(ax, last_row["date"])

    add_source_footer(
        fig,
        "Source: FRED (CFNAI, Federal Reserve Bank of Chicago) | Composite de 85 indicateurs "
        "d'activité | MA3 < -0.70 après expansion = signal récessif historique",
        as_of_date=last_row["date"],
    )

    period_label = get_current_period_label()
    out_dir = os.path.join(OUTPUT_DIR, period_label)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "30_cfnai_activity_index.png")

    finalize_chart(fig, ax, out_path, handles=[line_ma3, line_raw, line_thr])

    print(f"[30_cfnai_activity_index] Graphique sauvegardé: {out_path}")
    return out_path


if __name__ == "__main__":
    generate()
