from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation and extra whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def calculate_match_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate the cosine similarity between a resume and a job description
    using TF-IDF vectors. Returns a percentage (0-100).
    """
    if not resume_text or not jd_text:
        return 0.0

    clean_resume = preprocess_text(resume_text)
    clean_jd = preprocess_text(jd_text)

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_jd, clean_resume])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0


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
