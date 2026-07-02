# AI Resume Screening System

An AI-powered web application that parses resumes, matches them against job descriptions using NLP, ranks candidates, generates AI summaries, and exports PDF/Excel reports.

---

## Features

- Upload multiple resumes (PDF / DOCX)
- Automatic extraction of name, email, phone, skills, education, experience, certifications, location
- Paste or upload a Job Description
- TF-IDF cosine-similarity matching score per candidate
- Ranked candidate list (highest match first)
- AI-generated summaries (via Claude API, with a rule-based fallback if no key is set)
- Filter by skills, experience, education, certification, location
- Sort by match score, experience, name
- Global search across name/email/skills
- PDF and Excel report download
- Dashboard with statistics
- SQLite database — zero external DB setup

---

## Tech Stack

| Layer    | Technology                              |
|----------|------------------------------------------|
| Backend  | Python 3.12, Flask                      |
| Database | SQLite                                  |
| Frontend | HTML5, CSS, JavaScript                  |
| NLP      | scikit-learn TF-IDF, pdfplumber, python-docx |
| AI       | Anthropic Claude API (optional)         |
| Reports  | ReportLab (PDF), openpyxl (Excel)       |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Ai-resume-analyser.git
cd Ai-resume-analyser
```

### 2. Create and activate a virtual environment

**Windows (VS Code terminal)**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Set your Anthropic API key

For real AI-generated summaries, set the environment variable:

**Windows**
```bash
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**macOS / Linux**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

If you skip this step, the system falls back to rule-based summaries — everything else works identically.

### 5. Run the application

```bash
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

---

## Running on Google Colab

```python
# Install dependencies
!pip install flask pdfplumber python-docx scikit-learn reportlab openpyxl anthropic werkzeug gunicorn

# Upload the project files/folder to Colab first, then run with pyngrok for a public URL:
!pip install pyngrok
from pyngrok import ngrok
import threading, subprocess

def run():
    subprocess.run(["python", "app.py"])

t = threading.Thread(target=run)
t.start()

public_url = ngrok.connect(5000)
print("Public URL:", public_url)
```

---

## Folder Structure

Flask is configured with `template_folder="."` and `static_folder="."`, so HTML, CSS, and JS live at the project root rather than in separate `templates/`/`static/` directories. `/css` and `/js` are served via custom routes in `app.py`.

```
Ai-resume-analyser/
├── app.py                  # Main Flask application & routes
├── config.py                # Configuration (paths, secret key, upload limits)
├── requirements.txt         # Python dependencies
├── render.yaml               # Render.com deployment config
├── README.md
├── base.html                 # Shared layout template
├── login.html
├── register.html
├── dashboard.html
├── upload.html
├── results.html
├── report.html
├── style.css / css/style.css
├── script.js / js/script.js
├── database.py               # (root-level copy)
├── parser.py, matcher.py, summarizer.py, filter.py, report.py, auth.py
├── models/
│   ├── database.py           # Schema & connection
│   ├── auth.py                # Registration & login
│   ├── parser.py              # PDF/DOCX parsing & NLP extraction
│   ├── matcher.py             # TF-IDF matching & ranking
│   ├── summarizer.py          # AI summary (Claude API / fallback)
│   ├── filter.py               # Filtering & sorting logic
│   └── report.py               # PDF & Excel generation
├── database/                 # SQLite database (auto-created)
├── uploads/                  # Uploaded resume files (auto-created)
└── reports/                  # Generated PDF/Excel reports (auto-created)
```

> **Note:** The repo currently has duplicate copies of several modules (e.g. `parser.py`, `matcher.py`) at both the project root and inside `models/`. `app.py` imports from `models.*`, so the `models/` versions are the ones actually in use — the root-level copies appear to be leftovers and can likely be removed once confirmed unused.

---

## Usage

1. Open the app at `http://127.0.0.1:5000`
2. Register an admin account (first time only)
3. Log in
4. Click **Upload Resumes** in the sidebar
5. Enter or upload a Job Description
6. Upload one or more resume files (PDF/DOCX)
7. Click **Start AI Screening**
8. View ranked candidates on the **Candidates** page
9. Use filters/search to narrow results
10. Download reports from the **Reports** page

---

## Deployment

A `render.yaml` is included for one-click deployment on [Render](https://render.com):
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Set `ANTHROPIC_API_KEY` and a strong `SECRET_KEY` as environment variables in the Render dashboard rather than relying on the defaults in the repo.

---

## Future Improvements

- Clean up duplicate root/`models/` module copies
- Email shortlisted candidates directly from the app
- Multi-user roles (recruiter, viewer)
- Integration with LinkedIn / job board APIs
- Interview scheduling module
- Resume anonymisation for unbiased screening
- Bulk resume ZIP upload
- Dark mode UI
