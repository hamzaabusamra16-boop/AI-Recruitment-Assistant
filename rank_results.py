
import json
from pathlib import Path

from AI.ranking import rank_candidates


BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / ".env_" / "candidates.json"
RANKED_FILE = BASE_DIR / ".env_" / "ranked_candidates.json"


def main():
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        candidates = json.load(file)

    ranking_result = rank_candidates(candidates, top_n=20)

    with open(RANKED_FILE, "w", encoding="utf-8") as file:
        json.dump(
            ranking_result,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Total candidates: {len(candidates)}")
    print(f"Qualified candidates: {sum(c['ranking']['all_must_have_satisfied'] for c in ranking_result['candidates'])}")
    print(f"Shortlisted candidates: {len(ranking_result['shortlist'])}")
    print(f"Saved ranking to: {RANKED_FILE}")


if __name__ == "__main__":
    main()
