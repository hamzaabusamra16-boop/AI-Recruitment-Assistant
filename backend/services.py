
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_FILE = BASE_DIR / ".env_" / "ranked_candidates.json"
ENV_DIR = BASE_DIR / ".env_"
DECISIONS_FILE = ENV_DIR / "candidate_decisions.json"
import sys

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from AI.ranking import rank_candidates

def load_ranked_candidates():
    if not RESULTS_FILE.exists():
        return []

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        return data.get("candidates", [])

    return data


def rank_saved_candidates(top_n=20):
    candidates = load_ranked_candidates()

    ranking_result = rank_candidates(
        candidates,
        top_n=top_n,
    )

    ENV_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            ranking_result,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return ranking_result

def load_candidate_decisions():
    if not DECISIONS_FILE.exists():
        return {}

    with open(DECISIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_candidate_decision(candidate_id, decision, notes=""):
    decisions = load_candidate_decisions()

    decisions[candidate_id] = {
        "decision": decision,
        "notes": notes,
    }

    ENV_DIR.mkdir(parents=True, exist_ok=True)

    with open(DECISIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            decisions,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return decisions[candidate_id]
