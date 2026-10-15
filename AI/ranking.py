
def rank_candidates(candidates, top_n=20):
    ranked = []

    for item in candidates:
        comparison = item.get("comparison", {})
        must_have = item.get("must_have", {})

        mandatory_results = must_have.get("results", [])
        all_mandatory_satisfied = (
            bool(mandatory_results)
            and all(
                result.get("is_satisfied", False)
                for result in mandatory_results
            )
        )

        skills = comparison.get("skills", {})
        education = comparison.get("education", {})
        certificates = comparison.get("certificates", {})

        skill_results = skills.get("results", [])
        education_results = education.get("results", [])
        certificate_results = certificates.get("results", [])

        all_results = (
            skill_results
            + education_results
            + certificate_results
        )

        total = len(all_results)
        met = sum(
            result.get("status") == "Meets"
            for result in all_results
        )

        score = (met / total * 100) if total else 0

        ranked.append({
            **item,
            "ranking": {
                "score": round(score, 2),
                "all_must_have_satisfied": all_mandatory_satisfied,
                "category": (
                    "Qualified"
                    if all_mandatory_satisfied
                    else "HR Review"
                ),
            },
        })

    ranked.sort(
        key=lambda item: (
            item["ranking"]["all_must_have_satisfied"],
            item["ranking"]["score"],
        ),
        reverse=True,
    )

    return {
        "candidates": ranked,
        "shortlist": [
            item for item in ranked
            if item["ranking"]["all_must_have_satisfied"]
        ][:top_n],
    }
