import os
import json
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, send_from_directory
)
from werkzeug.utils import secure_filename
from config import Config
from models.database import init_db, get_connection
from models.auth import register_admin, login_admin
from models.parser import parse_resume
from models.matcher import batch_match_and_rank, calculate_match_score
from models.summarizer import generate_ai_summary
from models.filter import filter_candidates, sort_candidates
from models.report import generate_pdf_report, generate_excel_report

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.root_path, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.root_path, 'js'), filename)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)

# Initialise database on startup
with app.app_context():
    init_db()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator to protect routes that require a logged-in admin."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def get_dashboard_stats() -> dict:
    """Compute stats shown on the dashboard."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM candidates")
        total_resumes = cursor.fetchone()["cnt"]

        cursor.execute("SELECT AVG(match_score) as avg FROM candidates WHERE match_score > 0")
        avg_row = cursor.fetchone()
        avg_score = round(avg_row["avg"] or 0, 1)

        cursor.execute(
            "SELECT name, match_score FROM candidates WHERE match_score > 0 ORDER BY match_score DESC LIMIT 1"
        )
        top = cursor.fetchone()
        top_candidate = dict(top) if top else None

        # Top skills: aggregate from all candidates
        cursor.execute("SELECT skills FROM candidates WHERE skills IS NOT NULL AND skills != ''")
        all_skills = {}
        for row in cursor.fetchall():
            for skill in row["skills"].split(","):
                skill = skill.strip()
                if skill:
                    all_skills[skill] = all_skills.get(skill, 0) + 1
        top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:8]

        # Match score distribution for chart
        cursor.execute("SELECT name, match_score FROM candidates WHERE match_score > 0 ORDER BY match_score DESC LIMIT 10")
        chart_data = [dict(r) for r in cursor.fetchall()]

        return {
            "total_resumes": total_resumes,
            "avg_score": avg_score,
            "top_candidate": top_candidate,
            "top_skills": top_skills,
            "chart_data": chart_data,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Authentication routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "admin_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        result = login_admin(username, password)
        if result["success"]:
            session["admin_id"] = result["admin"]["id"]
            session["admin_name"] = result["admin"]["full_name"]
            session["admin_username"] = result["admin"]["username"]
            flash(f"Welcome back, {result['admin']['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(result["error"], "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not all([full_name, email, username, password, confirm_password]):
            flash("All fields are required.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        else:
            result = register_admin(full_name, email, username, password)
            if result["success"]:
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
            else:
                flash(result["error"], "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


# ---------------------------------------------------------------------------
# Upload Resumes
# ---------------------------------------------------------------------------

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        jd_text = request.form.get("jd_text", "").strip()
        jd_title = request.form.get("jd_title", "Job Position").strip()

        # Handle JD file upload
        jd_file = request.files.get("jd_file")
        if jd_file and jd_file.filename:
            jd_filename = secure_filename(jd_file.filename)
            jd_path = os.path.join(Config.UPLOAD_FOLDER, "jd_" + jd_filename)
            jd_file.save(jd_path)
            from models.parser import extract_text
            jd_text = extract_text(jd_path)

        if not jd_text:
            flash("Please provide a Job Description (text or file).", "danger")
            return redirect(url_for("upload"))

        # Save JD to database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO job_descriptions (title, content, uploaded_by) VALUES (?, ?, ?)",
            (jd_title, jd_text, session["admin_id"])
        )
        jd_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Process uploaded resume files
        files = request.files.getlist("resumes")
        if not files or all(f.filename == "" for f in files):
            flash("Please upload at least one resume.", "danger")
            return redirect(url_for("upload"))

        uploaded_count = 0
        errors = []

        for file in files:
            if file.filename == "":
                continue
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: unsupported format (use PDF or DOCX).")
                continue

            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            try:
                # Parse resume
                parsed = parse_resume(filepath)
                # Match against JD
                score = calculate_match_score(parsed["raw_text"], jd_text)
                parsed["match_score"] = score

                # Save candidate to DB (rank will be updated after all are processed)
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO candidates
                    (filename, filepath, name, email, phone, skills, education, experience,
                     certifications, location, raw_text, match_score, job_description_id, uploaded_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename, filepath,
                    parsed["name"], parsed["email"], parsed["phone"],
                    parsed["skills"], parsed["education"], parsed["experience"],
                    parsed["certifications"], parsed["location"], parsed["raw_text"],
                    score, jd_id, session["admin_id"]
                ))
                conn.commit()
                conn.close()
                uploaded_count += 1
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")

        # Re-rank all candidates for this JD
        _rerank_candidates(jd_id)

        # Generate AI summaries
        _generate_summaries_for_jd(jd_id, jd_text)

        if errors:
            for err in errors:
                flash(err, "warning")

        if uploaded_count > 0:
            flash(f"{uploaded_count} resume(s) processed and ranked successfully!", "success")
            return redirect(url_for("results", jd_id=jd_id))
        else:
            flash("No valid resumes were processed.", "danger")
            return redirect(url_for("upload"))

    return render_template("upload.html")


def _rerank_candidates(jd_id: int):
    """Fetch all candidates for a JD, rank them, and update the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, match_score FROM candidates WHERE job_description_id = ? ORDER BY match_score DESC",
        (jd_id,)
    )
    rows = cursor.fetchall()
    for rank, row in enumerate(rows, start=1):
        cursor.execute("UPDATE candidates SET rank = ? WHERE id = ?", (rank, row["id"]))
    conn.commit()
    conn.close()


def _generate_summaries_for_jd(jd_id: int, jd_text: str):
    """Generate AI summaries for all candidates belonging to a JD."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE job_description_id = ?", (jd_id,))
    candidates = [dict(row) for row in cursor.fetchall()]
    conn.close()

    for c in candidates:
        summary = generate_ai_summary(c, jd_text)
        conn = get_connection()
        conn.execute("UPDATE candidates SET ai_summary = ? WHERE id = ?", (summary, c["id"]))
        conn.commit()
        conn.close()


# ---------------------------------------------------------------------------
# Results / Ranking
# ---------------------------------------------------------------------------

@app.route("/results")
@login_required
def results():
    jd_id = request.args.get("jd_id", type=int)
    search = request.args.get("search", "")
    sort_by = request.args.get("sort", "rank")
    filter_skills = request.args.get("skills", "")
    filter_experience = request.args.get("experience", "")
    filter_education = request.args.get("education", "")
    filter_cert = request.args.get("certification", "")
    filter_location = request.args.get("location", "")

    conn = get_connection()
    cursor = conn.cursor()

    if jd_id:
        cursor.execute("SELECT * FROM candidates WHERE job_description_id = ?", (jd_id,))
    else:
        cursor.execute("SELECT * FROM candidates")

    candidates = [dict(row) for row in cursor.fetchall()]

    # Fetch JD list for selector
    cursor.execute("SELECT id, title, created_at FROM job_descriptions ORDER BY created_at DESC")
    jd_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Apply filters
    filters = {
        "skills": filter_skills,
        "experience": filter_experience,
        "education": filter_education,
        "certification": filter_cert,
        "location": filter_location,
        "search": search,
    }
    candidates = filter_candidates(candidates, filters)
    candidates = sort_candidates(candidates, sort_by)

    return render_template(
        "results.html",
        candidates=candidates,
        jd_list=jd_list,
        selected_jd=jd_id,
        sort_by=sort_by,
        filters=filters,
        search=search,
    )


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@app.route("/report")
@login_required
def report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY generated_at DESC LIMIT 20")
    reports = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT id, title FROM job_descriptions ORDER BY created_at DESC")
    jd_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("report.html", reports=reports, jd_list=jd_list)


@app.route("/report/generate/pdf")
@login_required
def generate_pdf():
    jd_id = request.args.get("jd_id", type=int)
    try:
        filepath = generate_pdf_report(session["admin_id"], jd_id)
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        flash(f"PDF generation failed: {e}", "danger")
        return redirect(url_for("report"))


@app.route("/report/generate/excel")
@login_required
def generate_excel():
    jd_id = request.args.get("jd_id", type=int)
    try:
        filepath = generate_excel_report(session["admin_id"], jd_id)
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
    except Exception as e:
        flash(f"Excel generation failed: {e}", "danger")
        return redirect(url_for("report"))


# ---------------------------------------------------------------------------
# API endpoint for dashboard chart data
# ---------------------------------------------------------------------------

@app.route("/api/stats")
@login_required
def api_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)


# ---------------------------------------------------------------------------
# Delete candidate
# ---------------------------------------------------------------------------

@app.route("/candidate/delete/<int:candidate_id>", methods=["POST"])
@login_required
def delete_candidate(candidate_id):
    conn = get_connection()
    conn.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    flash("Candidate removed.", "info")
    return redirect(url_for("results"))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
