import re


def filter_candidates(candidates: list, filters: dict) -> list:
    """
    Filter a list of candidate dicts based on the provided filter criteria.

    filters keys (all optional, empty string = no filter):
        skills      - comma-separated skills to look for
        experience  - minimum years (integer string)
        education   - keyword (e.g. 'bachelor', 'master')
        certification - keyword
        location    - keyword
        search      - global search across name, email, skills
    """
    result = []

    skill_filter = [s.strip().lower() for s in filters.get("skills", "").split(",") if s.strip()]
    experience_filter = filters.get("experience", "").strip()
    education_filter = filters.get("education", "").strip().lower()
    cert_filter = filters.get("certification", "").strip().lower()
    location_filter = filters.get("location", "").strip().lower()
    search_query = filters.get("search", "").strip().lower()

    for candidate in candidates:
        # --- skills filter ---
        if skill_filter:
            candidate_skills = candidate.get("skills", "").lower()
            if not any(sk in candidate_skills for sk in skill_filter):
                continue

        # --- experience filter (min years) ---
        if experience_filter:
            try:
                min_years = int(experience_filter)
                exp_text = candidate.get("experience", "")
                numbers = re.findall(r"\d+", exp_text)
                candidate_years = int(numbers[0]) if numbers else 0
                if candidate_years < min_years:
                    continue
            except ValueError:
                pass

        # --- education filter ---
        if education_filter:
            if education_filter not in candidate.get("education", "").lower():
                continue

        # --- certification filter ---
        if cert_filter:
            if cert_filter not in candidate.get("certifications", "").lower():
                continue

        # --- location filter ---
        if location_filter:
            if location_filter not in candidate.get("location", "").lower():
                continue

        # --- global search ---
        if search_query:
            searchable = " ".join([
                candidate.get("name", ""),
                candidate.get("email", ""),
                candidate.get("skills", ""),
            ]).lower()
            if search_query not in searchable:
                continue

        result.append(candidate)

    return result


def sort_candidates(candidates: list, sort_by: str = "rank") -> list:
    """
    Sort candidates by the given field.
    sort_by options: 'rank', 'highest_match', 'lowest_match', 'experience', 'name'
    """
    if sort_by == "highest_match":
        return sorted(candidates, key=lambda c: c.get("match_score", 0), reverse=True)
    elif sort_by == "lowest_match":
        return sorted(candidates, key=lambda c: c.get("match_score", 0))
    elif sort_by == "experience":
        def _exp_key(c):
            nums = re.findall(r"\d+", c.get("experience", "0"))
            return int(nums[0]) if nums else 0
        return sorted(candidates, key=_exp_key, reverse=True)
    elif sort_by == "name":
        return sorted(candidates, key=lambda c: c.get("name", "").lower())
    else:
        # Default: by rank ascending
        return sorted(candidates, key=lambda c: c.get("rank", 999))
