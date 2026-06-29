# AI Resume Screening System

An AI-powered web application that parses resumes, matches them against job descriptions using NLP, ranks candidates, generates AI summaries, and exports PDF/Excel reports.

---

## Features

- Upload multiple resumes (PDF / DOCX)
- Automatic extraction of name, email, phone, skills, education, experience, certifications, location
- Paste or upload a Job Description
- TF-IDF cosine-similarity matching score per candidate
- Ranked candidate list (highest match first)
- AI-generated summaries (via Claude API or rule-based fallback)
- Filter by skills, experience, education, certification, location
- Sort by match score, experience, name
- Global search across name/email/skills
- PDF and Excel report download
- Dashboard with Chart.js statistics
- SQLite database – zero external DB setup

---

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Backend  | Python 3.12, Flask                      |
| Database | SQLite                                  |
| Frontend | HTML5, Bootstrap 5, Chart.js            |
| NLP      | scikit-learn TF-IDF, pdfplumber, docx   |
| AI       | Anthropic Claude API (optional)         |
| Reports  | ReportLab (PDF), openpyxl (Excel)       |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI-Resume-Screening-System.git
cd AI-Resume-Screening-System
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

If you skip this step, the system uses a rule-based summary fallback — everything else works identically.

### 5. Run the application

```bash
python app.py
```

Open your browser and navigate to: **http://127.0.0.1:5000**

---

## Running on Google Colab

```python
# Install dependencies
!pip install flask pdfplumber python-docx scikit-learn reportlab openpyxl anthropic werkzeug

# Mount if needed or upload files directly
# Then run with pyngrok for public URL:
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

```
AI-Resume-Screening-System/
├── app.py                  # Main Flask application
├── config.py               # Configuration (paths, keys)
├── requirements.txt        # Python dependencies
├── README.md
├── .gitignore
├── database/               # SQLite database (auto-created)
├── uploads/                # Uploaded resume files
├── reports/                # Generated PDF/Excel reports
├── models/
│   ├── auth.py             # Registration & login
│   ├── database.py         # Schema & connection
│   ├── filter.py           # Filtering & sorting logic
│   ├── matcher.py          # TF-IDF matching & ranking
│   ├── parser.py           # PDF/DOCX parsing & NLP extraction
│   ├── report.py           # PDF & Excel generation
│   └── summarizer.py       # AI summary (Claude API / fallback)
├── static/
│   ├── css/style.css
│   └── js/script.js
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── results.html
│   └── report.html
└── utils/
```

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
9. Use filters/search to narrow down
10. Download reports from the **Reports** page

---

## Screenshots

> _Add screenshots of Dashboard, Upload, Results, and Report pages here._

---

## Future Improvements

- Email shortlisted candidates directly from the app
- Multi-user roles (recruiter, viewer)
- Integration with LinkedIn / job board APIs
- Interview scheduling module
- Resume anonymisation for unbiased screening
- Bulk resume ZIP upload
- Dark mode UI
