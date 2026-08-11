"""
Génère, via l'API Anthropic (Claude), un court commentaire d'interprétation
pour chaque graphique de la période courante : que dit le graphique dans la
configuration actuelle des marchés, et qu'est-ce que ça implique pour le
comité d'investissement.

Le modèle reçoit le PNG généré (vision) plus le README du graphique comme
contexte, et rédige 3 à 5 phrases en français. Les commentaires sont écrits
dans output/{periode}/commentary.json, que compile_report.py affiche sous le
résumé statique du README, à côté de chaque graphique.

Usage :
    python generate_commentary.py                 # période courante
    python generate_commentary.py --period 2026S2 # période explicite

Philosophie de robustesse (projet sans maintenance) : ce script est un
enrichissement OPTIONNEL du rapport, jamais un point de panne.
  - Pas de clé ANTHROPIC_API_KEY -> le script sort proprement (code 0),
    compile_report.py se rabat sur les résumés statiques des README.
  - Erreur API sur un graphique -> graphique suivant ; l'éventuel
    commentaire de la période précédente déjà présent dans commentary.json
    est conservé plutôt qu'écrasé par du vide.
  - Le fichier commentary.json est réécrit après chaque graphique : une
    interruption en cours de route ne perd pas les commentaires déjà générés.
  - Le script se termine TOUJOURS avec le code 0 : une panne de l'API
    Anthropic ne doit jamais faire échouer le workflow de génération.
"""
import os
import re
import json
import base64
import argparse

from common.config import (
    ANTHROPIC_API_KEY, OUTPUT_DIR, PROJECT_ROOT, get_current_period_label,
)

CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")

# Modèle par défaut, surchargeable sans toucher au code le jour où ce modèle
# sera retiré du catalogue (variable d'environnement dans le workflow).
DEFAULT_MODEL = "claude-opus-5"
MODEL = os.environ.get("COMMENTARY_MODEL", DEFAULT_MODEL)

# Longueur maximale d'un commentaire dans le rapport (caractères). Le prompt
# demande plus court ; cette borne est le garde-fou si le modèle déborde.
MAX_COMMENTARY_CHARS = 900

SYSTEM_PROMPT = (
    "Tu es analyste senior de l'équipe de recherche macroéconomique d'une "
    "banque d'investissement. Tu rédiges, en français, les commentaires de "
    "marché qui accompagnent chaque graphique de la note remise au comité "
    "d'investissement. Ton style est factuel, précis et sans emphase."
)

USER_PROMPT_TEMPLATE = """Voici un graphique de notre note de recherche (période {periode}), accompagné de sa fiche interne :

{readme}

Rédige le commentaire d'interprétation destiné au comité d'investissement : que montre ce graphique dans la configuration ACTUELLE (dernier point, tendance récente, niveau par rapport à l'historique visible), et qu'est-ce que ça implique concrètement ?

Contraintes impératives :
- Un seul paragraphe de 3 à 5 phrases, 600 caractères maximum.
- Appuie-toi uniquement sur ce qui est visible dans l'image et sur la fiche : ne cite aucun chiffre ou événement qui n'y figure pas.
- Texte brut uniquement : pas de titre, pas de liste, pas de gras, pas de markdown.
- Ne décris pas le graphique (le lecteur l'a sous les yeux) : interprète-le."""


def _discover_charts():
    """Liste triée des dossiers charts/NN_nom/ (même logique que compile_report)."""
    entries = []
    for name in sorted(os.listdir(CHARTS_DIR)):
        path = os.path.join(CHARTS_DIR, name)
        if os.path.isdir(path) and re.match(r"^\d{2}_", name):
            entries.append(name)
    return entries


def _read_readme(chart_dir: str) -> str:
    path = os.path.join(CHARTS_DIR, chart_dir, "README.md")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _find_png(charts_output_dir: str, chart_dir: str):
    num_prefix = chart_dir[:2]
    for f in sorted(os.listdir(charts_output_dir)):
        if f.startswith(num_prefix) and f.endswith(".png"):
            return os.path.join(charts_output_dir, f)
    return None


def _sanitize(text: str) -> str:
    """
    Garde-fous de forme sur la réponse du modèle : texte brut, un paragraphe,
    longueur bornée. Le rapport PDF doit rester lisible quel que soit le
    comportement du modèle dans plusieurs années.
    """
    # Retire un éventuel habillage markdown malgré la consigne.
    text = re.sub(r"^#+\s.*$", "", text, flags=re.MULTILINE)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    # Un seul paragraphe : les sauts de ligne deviennent des espaces.
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > MAX_COMMENTARY_CHARS:
        # Tronque à la dernière fin de phrase avant la borne, pour ne jamais
        # couper un commentaire au milieu d'un mot dans le rapport.
        cut = text[:MAX_COMMENTARY_CHARS]
        last_period = cut.rfind(". ")
        text = cut[: last_period + 1] if last_period > 200 else cut.rstrip() + "…"
    return text


def _generate_one(client, chart_dir: str, png_path: str, period_label: str) -> str:
    """Appelle l'API pour un graphique et retourne le commentaire nettoyé."""
    with open(png_path, "rb") as f:
        png_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    readme = _read_readme(chart_dir) or "(pas de fiche disponible)"
    user_prompt = USER_PROMPT_TEMPLATE.format(periode=period_label, readme=readme)

    # Streaming + get_final_message : évite les timeouts de requête sans
    # avoir à gérer les événements un par un.
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": png_b64,
                    },
                },
                {"type": "text", "text": user_prompt},
            ],
        }],
    ) as stream:
        message = stream.get_final_message()

    # Avec le thinking activé, la réponse contient des blocs "thinking" puis
    # des blocs "text" : seuls ces derniers forment le commentaire.
    text = "".join(
        block.text for block in message.content if getattr(block, "type", "") == "text"
    )
    commentary = _sanitize(text)
    if not commentary:
        raise RuntimeError("réponse vide après nettoyage")
    return commentary


def generate_all(period_label: str = None):
    if period_label is None:
        period_label = get_current_period_label()

    charts_output_dir = os.path.join(OUTPUT_DIR, period_label)
    if not os.path.isdir(charts_output_dir):
        print(f"[commentary] Dossier introuvable: {charts_output_dir} -- "
              "lance d'abord run_all.py. Rien à faire.")
        return

    if not ANTHROPIC_API_KEY:
        print("[commentary] ANTHROPIC_API_KEY absente -- commentaires ignorés, "
              "le rapport utilisera les résumés statiques des README.")
        return

    try:
        import anthropic
    except ImportError:
        print("[commentary] Le paquet 'anthropic' n'est pas installé "
              "(pip install -r requirements.txt) -- commentaires ignorés.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=3)

    commentary_path = os.path.join(charts_output_dir, "commentary.json")
    commentaries = {}
    if os.path.exists(commentary_path):
        try:
            with open(commentary_path, "r", encoding="utf-8") as f:
                commentaries = json.load(f)
        except (json.JSONDecodeError, OSError):
            print("[commentary] commentary.json existant illisible -- reparti de zéro.")
            commentaries = {}

    from datetime import datetime
    commentaries["_meta"] = {
        "generated_at": datetime.today().strftime("%d/%m/%Y"),
        "model": MODEL,
    }

    n_ok, n_err, n_skip = 0, 0, 0
    for chart_dir in _discover_charts():
        png_path = _find_png(charts_output_dir, chart_dir)
        if png_path is None:
            n_skip += 1
            continue

        try:
            commentaries[chart_dir] = _generate_one(
                client, chart_dir, png_path, period_label
            )
            n_ok += 1
            print(f"[commentary] ✓ {chart_dir}")
        except Exception as e:
            # Graphique suivant ; un éventuel commentaire déjà présent (run
            # précédent) est conservé plutôt qu'écrasé.
            n_err += 1
            print(f"[commentary] ✗ {chart_dir}: {type(e).__name__}: {e}")

        # Écriture incrémentale : une interruption ne perd pas l'acquis.
        with open(commentary_path, "w", encoding="utf-8") as f:
            json.dump(commentaries, f, ensure_ascii=False, indent=2)

    print(f"[commentary] Terminé : {n_ok} générés, {n_err} en erreur, "
          f"{n_skip} sans PNG cette période. -> {commentary_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Génère les commentaires IA des graphiques de la période."
    )
    parser.add_argument("--period", default=None,
                        help="Période, ex: 2026S2 (défaut: période courante)")
    args = parser.parse_args()
    try:
        generate_all(period_label=args.period)
    except Exception as e:
        # Enrichissement optionnel : jamais un point de panne du workflow.
        print(f"[commentary] ERREUR globale non bloquante: {type(e).__name__}: {e}")
