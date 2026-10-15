import re
from .similarity import compare_requirement_similarity
def comparison_skills( candidate_skills, required_skills, cv_text="", candidate_experience=None, candidate_projects=None):
    results = []

    normalized_candidate = [
        skill.strip().lower()
        for skill in (candidate_skills or [])
        if isinstance(skill, str)
    ]

    evidence_sections = []

    for section_name, items in [
        ("experience", candidate_experience or []),
        ("project", candidate_projects or [])
    ]:
        for item in items:
            if isinstance(item, str):
                text = item.strip()
            elif isinstance(item, dict):
                text = " ".join(
                    str(item.get(key, ""))
                    for key in [
                        "title",
                        "role",
                        "description",
                        "responsibilities",
                        "technologies",
                        "skills"
                    ]
                    if item.get(key)
                ).strip()
            else:
                continue

            if text:
                evidence_sections.append({
                    "section": section_name,
                    "text": text
                })

    for skill in (required_skills or []):
        if not isinstance(skill, str) or not skill.strip():
            continue

        normalized_skill = skill.strip().lower()

        if normalized_skill in normalized_candidate:
            results.append({
                "requirement": skill,
                "status": "Meets",
                "evidence": skill,
                "similarity_score": None
            })
            continue

        normalized_cv = (cv_text or "").lower()

        if normalized_skill in normalized_cv:
            results.append({
                "requirement": skill,
                "status": "Meets",
                "evidence": skill,
                "similarity_score": None
            })
            continue

        best_match = None

        for item in evidence_sections:
            score = compare_requirement_similarity(
                skill,
                item["text"]
            )

            if best_match is None or score > best_match["score"]:
                best_match = {
                    "score": score,
                    "text": item["text"],
                    "section": item["section"]
                }

        if best_match and best_match["score"] >= 50:
            status = "Partially Meets"
            evidence = {
                "section": best_match["section"],
                "text": best_match["text"]
            }
            score = best_match["score"]
        else:
            status = "No Evidence Found"
            evidence = None
            score = best_match["score"] if best_match else None

        results.append({
            "requirement": skill,
            "status": status,
            "evidence": evidence,
            "similarity_score": score
        })

    matched_count = sum(
        result["status"] == "Meets"
        for result in results
    )

    return {
        "results": results,
        "match_percentage": (
            matched_count / len(results) * 100
            if results else 0
        )
    }

def compare_experience(candidate_years, required_years, evidence=None):
    if candidate_years is None or required_years is None:
        return {
            "status": "No Evidence Found",
            "candidate_years": candidate_years,
            "required_years": required_years,
            "evidence": evidence
        }

    if candidate_years >= required_years:
        status = "Meets"
    else:
        status = "Does Not Meet"

    return {
        "status": status,
        "candidate_years": candidate_years,
        "required_years": required_years,
        "evidence": evidence
    }


def compare_education(candidate_education, required_field):
    results = []

    for requirement in required_field:
        required_words = set(
            re.findall(r"\b[a-z0-9]+\b", requirement.lower())
        ) - {"in", "of", "and", "the", "a", "an"}

        matched_education = []

        for education in candidate_education:
            degree = education.get("degree") or ""
            field = education.get("field_of_study") or ""

            candidate_text = f"{degree} {field}".lower()
            candidate_words = set(
                re.findall(r"\b[a-z0-9]+\b", candidate_text)
            )

            if required_words and required_words.issubset(candidate_words):
                matched_education.append({
                    "degree": degree,
                    "field_of_study": field,
                    "institution": education.get("institution")
                })

        if matched_education:
            status = "Meets"
            evidence = matched_education
        else:
            status = "No Evidence Found"
            evidence = None

        results.append({
            "requirement": requirement,
            "status": status,
            "evidence": evidence
        })

    return {"results": results}
def compare_certificates(candidate_certificates, required_certificates):
    results = []

    normalized_candidate = [
        certificate.strip().lower()
        for certificate in candidate_certificates
        if isinstance(certificate, str)
    ]

    for certificate in required_certificates:
        normalized_certificate = certificate.strip().lower()

        if normalized_certificate in normalized_candidate:
            status = "Meets"
            evidence = certificate
        else:
            status = "No Evidence Found"
            evidence = None

        results.append({
            "requirement": certificate,
            "status": status,
            "evidence": evidence
        })

    matched_count = sum(
        result["status"] == "Meets"
        for result in results
    )

    return {
        "results": results,
        "match_percentage": (
            matched_count / len(required_certificates) * 100
            if required_certificates else 0
        )
    }



def extract_required_years(requirements):
    for requirement in requirements:
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            requirement,
            re.IGNORECASE
        )
        if match:
            return float(match.group(1))

    return None

def extract_candidate_years(experience):
    total_years = 0.0
    found = False

    for item in experience:
        duration = item.get("duration") or ""

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
            duration,
            re.IGNORECASE
        )

        if match:
            total_years += float(match.group(1))
            found = True

    return total_years if found else None

def evaluate_must_have(must_have, comparison_results):
    results = []

    categories = [
        comparison_results.get("skills", {}).get("results", []),
        comparison_results.get("education", {}).get("results", []),
        comparison_results.get("certificates", {}).get("results", []),
    ]

    for requirement in must_have or []:
        if not isinstance(requirement, str) or not requirement.strip():
            continue

        normalized = requirement.strip().lower()
        matched_result = None

        for category in categories:
            for result in category:
                evaluated = result.get("requirement", "").strip().lower()

                if normalized == evaluated:
                    matched_result = result
                    break

            if matched_result:
                break

        if any(word in normalized for word in ("experience", "years", "year")):
            experience = comparison_results.get("experience", {})
            status = experience.get("status", "No Evidence Found")
            evidence = experience.get("evidence")

        elif matched_result:
            status = matched_result.get("status", "No Evidence Found")
            evidence = matched_result.get("evidence")

        else:
            status = "No Evidence Found"
            evidence = None

        results.append({
            "requirement": requirement,
            "status": status,
            "evidence": evidence,
            "is_satisfied": status == "Meets",
        })

    return {
        "results": results,
        "all_must_have_satisfied": all(
            item["is_satisfied"] for item in results
        ),
    }
