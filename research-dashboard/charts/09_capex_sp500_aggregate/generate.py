"""
Graphique : Capex trimestriel par principaux contributeurs (3 dernières
années) + tendance annuelle (TTM)

Source : SEC EDGAR, endpoint `frames` (un concept XBRL donné, pour TOUTES
les entreprises, sur un trimestre donné, en un seul appel API).

Contrairement à la première version (capex agrégé total sur 10 ans), ce
chart se concentre sur les 3 dernières années en détail trimestriel, avec :
  1. Une décomposition par entreprise (barres empilées) pour voir QUI tire
     le capex agrégé -- typiquement dominé par une poignée d'hyperscalers
  2. Une ligne de tendance annuelle (somme glissante sur 12 mois, "TTM")
     superposée, pour lisser le bruit trimestriel et voir la dynamique
     annuelle sous-jacente

Concepts XBRL essayés (fusionnés, pas juste le premier qui répond -- voir
_get_merged_frame_for_period) -- voir common/config.py :
  - PaymentsToAcquirePropertyPlantAndEquipment
  - PaymentsForCapitalImprovements
  - PaymentsToAcquireProductiveAssets

Pourquoi c'est utile : le capex agrégé total (version précédente) ne dit pas
qui pousse la tendance. Avec l'explosion des dépenses d'infrastructure IA,
savoir si la hausse vient de 3-4 hyperscalers ou d'une base large
d'entreprises change complètement l'interprétation du signal macro.

Sortie : PNG dans output/{periode}/09_capex_sp500_aggregate.png
"""
import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from common.edgar_client import get_frame, get_ticker_to_cik_map
from common.chart_style import (
    setup_figure, add_source_footer, format_date_axis, add_freshness_subtitle, COLOR_ACCENT
)
from common.config import get_current_period_label, OUTPUT_DIR, CAPEX_XBRL_CONCEPTS, SP500_LARGE_CAP_SAMPLE

# Ce chart se concentre volontairement sur une fenêtre plus courte que les
# autres (3 ans au lieu de 10) pour rester lisible en détail trimestriel
# avec une décomposition par entreprise.
DISPLAY_YEARS = 3
TOP_N = 6

# Palette pour les entreprises + "Autres" (dernière couleur = Autres, gris neutre)
BAR_COLORS = ["#1a3a5c", "#2f6690", "#5b8ab8", "#8fb8d8", "#c0392b", "#e08e79", "#bbbbbb"]
COLOR_TTM_LINE = "#222222"


def _quarter_end_date(year: int, quarter: int) -> pd.Timestamp:
    """Retourne la date de fin du trimestre donné (dernier jour du mois)."""
    month = quarter * 3
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _get_merged_frame_for_period(period: str) -> dict:
    """
    Interroge TOUS les concepts XBRL candidats pour une période donnée et
    fusionne les résultats par CIK (au lieu de s'arrêter au premier concept
    qui renvoie des données pour N'IMPORTE QUELLE entreprise).

    Bug corrigé : l'ancienne version prenait le PREMIER concept renvoyant des
    données globalement, puis abandonnait les autres concepts pour cette
    période -- ce qui excluait silencieusement, sur TOUTE la fenêtre, toute
    entreprise taguant son capex avec un
