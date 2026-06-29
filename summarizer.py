import anthropic
from config import Config


def generate_ai_summary(candidate: dict, jd_text: str = "") -> str:
    """
    Use Claude to generate a structured AI summary for a candidate.
    Falls back to a rule-based summary if the API key is not set.
    """
    if Config.ANTHROPIC_API_KEY:
        return _summary_via_claude(candidate, jd_text)
    return _summary_rule_based(candidate)


def _summary_via_claude(candidate: dict, jd_text: str) -> str:
    """Call the Anthropic Messages API to generate a candidate summary."""
    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    prompt = f"""You are an expert HR recruiter reviewing a candidate for a job opening.

Candidate Details:
- Name: {candidate.get('name', 'N/A')}
- Skills: {candidate.get('skills', 'N/A')}
- Education: {candidate.get('education', 'N/A')}
- Experience: {candidate.get('experience', 'N/A')}
- Certifications: {candidate.get('certifications', 'N/A')}
- Location: {candidate.get('location', 'N/A')}
- Match Score: {candidate.get('match_score', 0):.1f}%

Job Description:
{jd_text[:1000] if jd_text else 'Not provided'}

Generate a concise professional summary covering:
1. Key Skills (bullet list, max 5)
2. Years of Experience
3. Strengths (2-3 points)
4. Weaknesses or Gaps (1-2 points)
5. Overall Suitability (1 sentence verdict)

Keep it under 200 words. Use plain text, no markdown."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        return _summary_rule_based(candidate) + f"\n[AI note: {e}]"


def _summary_rule_based(candidate: dict) -> str:
    """Generate a structured summary without an API call."""
    name = candidate.get("name", "Candidate")
    skills = candidate.get("skills", "Not listed")
    experience = candidate.get("experience", "Not specified")
    education = candidate.get("education", "Not specified")
    certs = candidate.get("certifications", "None")
    score = candidate.get("match_score", 0)

    skill_list = skills.split(", ")[:5]
    skill_text = ", ".join(skill_list) if skill_list else "No specific skills detected"

    if score >= 75:
        suitability = "Strong candidate – highly recommended for interview."
    elif score >= 50:
        suitability = "Moderate fit – consider for review with additional context."
    else:
        suitability = "Low match – may not meet the core requirements."

    summary = (
        f"Key Skills: {skill_text}. "
        f"Experience: {experience}. "
        f"Education: {education}. "
        f"Certifications: {certs}. "
        f"Overall Suitability: {suitability} "
        f"(Match Score: {score:.1f}%)"
    )
    return summary
