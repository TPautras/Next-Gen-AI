import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]   # racine du dépôt (le script est dans td2/A-quorum/)

PANEL_3 = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]

QUORUM_5 = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free")
]


def propositions(rows, case, nature, panel):
    """Propositions des membres de `panel` pour une question : un membre sans réponse reste présent mais ne vote pas.

    The last CSV row per panel member is its last attempt. Use one chronological
    export per experiment; reject mixed experiments rather than merging them.
    References and correctness verdicts are not passed to the student's vote.
    """
    selected = {}
    for row in rows:
        key = (row["provider"], row["model_requested"])
        if row["case_id"] == case and row["nature"] == nature and key in panel:
            selected[key] = row
    proposals = []
    for provider, model in panel:
        row = selected.get((provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value not in {None, ""}
        proposals.append(SimpleNamespace(provider=provider, model_requested=model,
                                         value=int(value) if valid else None,
                                         verdict="executed" if valid else "error"))
    return proposals


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", ROOT / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)

def en_texte(resultat):
    """Résultat du vote -> texte lisible pour le tableau."""
    if resultat["consensus"]:
        return f"consensus {resultat['value']} ({resultat['votes']} voix)"
    return f"abstention ({resultat['votes']} voix max)"


def accord(resultat, reference):
    """La décision est-elle juste ? Une abstention n'est ni juste ni fausse : rien n'a été publié."""
    if not resultat["consensus"]:
        return "—"
    if resultat["value"] == reference:
        return "oui"
    return "non"


def tableau():
    """Imprime le tableau Markdown des 20 questions (2 sur 3 contre 3 sur 5), puis le détail des questions qui changent."""
    rows = list(csv.DictReader(open(ROOT / "traces-td1.csv", encoding="utf-8")))
    references = {}   # case_id -> valeur de référence en centimes
    for ligne in csv.DictReader(open(ROOT / "reference-td1.csv", encoding="utf-8")):
        references[ligne["case_id"]] = int(ligne["revenue_cents"])
    vote = load_vote()

    print("| Question | Référence | 2 sur 3 (panel fixe) | Accord | 3 sur 5 (5 modèles) | Accord | Change ? |")
    print("|---|---|---|---|---|---|---|")
    questions_qui_changent = []
    for case in sorted(references):
        ref = references[case]
        r3 = vote(propositions(rows, case, "real", PANEL_3), 2)
        r5 = vote(propositions(rows, case, "real", QUORUM_5), 3)
        # La décision change si l'un publie et l'autre s'abstient, ou si la valeur ou la marge diffère.
        change = r3["consensus"] != r5["consensus"] or r3["value"] != r5["value"]
        marge = not change and not r3["consensus"] and r3["votes"] != r5["votes"]
        if change or marge:
            questions_qui_changent.append(case)
        marque = "**décision**" if change else ("marge" if marge else "")
        print(f"| {case} | {ref} | {en_texte(r3)} | {accord(r3, ref)} | {en_texte(r5)} | {accord(r5, ref)} | {marque} |")

    # Détail des 5 propositions pour les questions qui changent : c'est ce qu'il faut commenter dans le rapport.
    for case in questions_qui_changent:
        print(f"\n{case} (référence {references[case]}) :")
        for p in propositions(rows, case, "real", QUORUM_5):
            print(f"  {p.provider}:{p.model_requested}  valeur={p.value}  verdict={p.verdict}")


if __name__ == "__main__":
    tableau()
