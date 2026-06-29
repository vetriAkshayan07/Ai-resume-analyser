import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai-resume-screening-secret-2024")

    # SQLite database path
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "resume_screening.db")

    # Upload folder for resumes
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # Reports output folder
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

    # Allowed resume file extensions
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Max upload size: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Anthropic API key (set via env variable or paste directly for local dev)
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
