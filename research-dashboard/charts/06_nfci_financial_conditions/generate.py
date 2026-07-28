"""
STUB - squelette à compléter.

Suivre la même structure que charts/01_real_fed_funds_rate/generate.py
ou charts/02_sahm_rule/generate.py :

1. Récupérer les données via common.fred_client.get_series() et/ou
   common.edgar_client (get_company_facts, get_frame, extract_concept_series)
2. Calculer la transformation nécessaire (ratio, YoY, z-score, spread...)
3. Tracer avec common.chart_style (setup_figure, add_recession_bands,
   format_date_axis, add_source_footer)
4. Sauvegarder dans output/{periode}/ via common.config.get_current_period_label()
   et common.config.OUTPUT_DIR

Voir le README.md de ce dossier pour le détail des séries et du calcul prévu.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def generate():
    raise NotImplementedError(
        "Ce graphique n'est pas encore implémenté. Voir le README.md de ce dossier."
    )


if __name__ == "__main__":
    generate()
