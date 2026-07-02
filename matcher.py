import math
import re
from collections import Counter


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation and extra whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _token_counter(text: str) -> Counter:
    return Counter(preprocess_text(text).split())


def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate a lightweight cosine similarity score between a resume and job description.
    Returns a percentage (0-100).
    """
    if not resume_text or not jd_text:
        return 0.0

    jd_counter = _token_counter(jd_text)
    resume_counter = _token_counter(resume_text)

    if not jd_counter or not resume_counter:
        return 0.0

    all_tokens = set(jd_counter) | set(resume_counter)
    if not all_tokens:
        return 0.0

    document_count = 2
    df = {token: 0 for token in all_tokens}
    for token in all_tokens:
        if token in jd_counter:
            df[token] += 1
        if token in resume_counter:
            df[token] += 1

    jd_tfidf = {}
    resume_tfidf = {}
    for token in all_tokens:
        idf = math.log((1 + document_count) / (1 + df[token])) + 1.0
        jd_tfidf[token] = jd_counter[token] * idf
        resume_tfidf[token] = resume_counter[token] * idf

    dot_product = sum(jd_tfidf[token] * resume_tfidf[token] for token in all_tokens)
    jd_norm = math.sqrt(sum(value * value for value in jd_tfidf.values()))
    resume_norm = math.sqrt(sum(value * value for value in resume_tfidf.values()))

    if jd_norm == 0 or resume_norm == 0:
        return 0.0

    score = dot_product / (jd_norm * resume_norm)
    return round(float(score) * 100, 2)


def rank_candidates(candidates: list) -> list:
    """
    Given a list of candidate dicts with 'match_score', assign rank
    in descending order and return the sorted list.
    """
    sorted_candidates = sorted(candidates, key=lambda c: c.get("match_score", 0), reverse=True)
    for i, candidate in enumerate(sorted_candidates, start=1):
        candidate["rank"] = i
    return sorted_candidates


def batch_match_and_rank(candidates: list, jd_text: str) -> list:
    """
    For a list of candidate dicts (each with 'raw_text'), compute match
    scores against jd_text and return them ranked.
    """
    for candidate in candidates:
        score = calculate_match_score(candidate.get("raw_text", ""), jd_text)
        candidate["match_score"] = score
    return rank_candidates(candidates)
