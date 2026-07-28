"""
Lance tous les generate.py de charts/*/ à la suite.

Usage:
    python run_all.py

Les noms de dossiers commencent par des chiffres (01_, 02_...), ce qui les
rend non importables comme modules Python classiques. On charge donc
chaque generate.py dynamiquement via importlib, par chemin de fichier.
"""
import os
import sys
import importlib.util
import traceback

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")


def load_and_run(chart_dir_name: str):
    generate_path = os.path.join(CHARTS_DIR, chart_dir_name, "generate.py")
    if not os.path.exists(generate_path):
        print(f"[{chart_dir_name}] SKIP — generate.py introuvable")
        return False

    spec = importlib.util.spec_from_file_location(f"chart_{chart_dir_name}", generate_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "generate"):
        print(f"[{chart_dir_name}] SKIP — pas de fonction generate()")
        return False

    try:
        module.generate()
        return True
    except NotImplementedError as e:
        print(f"[{chart_dir_name}] STUB non implémenté — {e}")
        return False
    except Exception:
        print(f"[{chart_dir_name}] ERREUR:")
        traceback.print_exc()
        return False


def main():
    chart_dirs = sorted(
        d for d in os.listdir(CHARTS_DIR)
        if os.path.isdir(os.path.join(CHARTS_DIR, d)) and not d.startswith("__")
    )

    print(f"=== Génération de {len(chart_dirs)} graphiques ===\n")

    results = {"ok": [], "stub": [], "erreur": []}
    for chart_dir in chart_dirs:
        print(f"--- {chart_dir} ---")
        success = load_and_run(chart_dir)
        if success:
            results["ok"].append(chart_dir)
        else:
            results["stub"].append(chart_dir)
        print()

    print("=== Résumé ===")
    print(f"Générés avec succès : {len(results['ok'])}")
    for c in results["ok"]:
        print(f"  ✓ {c}")
    print(f"Non générés (stub/erreur) : {len(results['stub'])}")
    for c in results["stub"]:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
