# backend/app.py
import os
import uuid
import shutil
import io
import tempfile
from flask import Flask, request, send_file, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

from transcriber import transcribe_audio_from_video
from analysis import analyze_text, compute_extra_metrics
from pdf_generator import generate_pdf
from models import init_db, SessionLocal, Report, Teacher, Base, engine
from forms import RegistrationForm, LoginForm

load_dotenv() # Load environment variables from .env

# ============================================================
# 1️⃣ Flask App Setup
# ============================================================
app = Flask(__name__, static_folder="templates/static", template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_very_secret_key_that_should_be_in_env')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # type: ignore

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    teacher = db.query(Teacher).get(int(user_id))
    db.close()
    return teacher

@app.before_request
def before_request():
    app.db = SessionLocal()

@app.teardown_request
def teardown_request(exception):
    if hasattr(app, "db"):
        app.db.close()

@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ============================================================
# 2️⃣ Authentication Routes
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db = app.db
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        teacher = Teacher(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            education_details=form.education_details.data,
            password_hash=hashed_password
        )
        db.add(teacher)
        db.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        db = app.db
        teacher = db.query(Teacher).filter_by(email=form.email.data).first()
        if teacher and check_password_hash(teacher.password_hash, form.password.data):
            login_user(teacher)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ============================================================
# 3️⃣ Reports Endpoints
# ============================================================
@app.route("/reports", methods=["GET"])
@login_required
def list_reports():
    db = app.db
    # Only fetch reports for the current logged-in teacher
    reports = db.query(Report).filter_by(teacher_id=current_user.id).all()
    return jsonify([
        {
            "id": r.id,
            "filename": r.filename,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in reports
    ])

@app.route("/report/<rid>")
@login_required
def get_report(rid):
    db = app.db
    report = db.query(Report).filter(Report.id == rid, Report.teacher_id == current_user.id).first()
    if not report:
        return jsonify({"error": "Report not found"}), 404

    return send_file(
        io.BytesIO(report.pdf_data),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{report.filename}_Evaluation.pdf"
    )

# ============================================================
# 4️⃣ Upload + Audio Extraction + Transcription + Analysis
# ============================================================
@app.route("/upload", methods=["POST"])
@login_required
def upload_and_analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    uid = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, file.filename)
    file.save(video_path)

    try:
        # 🔹 Extract audio & transcribe (pure Python Whisper)
        transcript_text, audio_path = transcribe_audio_from_video(
            video_path, uid, temp_dir
        )

        # 🔹 Analyze transcript
        rubric = analyze_text(transcript_text)
        extras = compute_extra_metrics(transcript_text, audio_path)
        rubric.update(extras)

        # 🔹 Generate PDF
        pdf_content = generate_pdf(rubric, transcript_text, source_filename=file.filename, teacher_info={
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
            'education_details': current_user.education_details
        })

        # 🔹 Save to SQLite
        db = app.db
        report = Report(
            id=uid,
            filename=file.filename,
            rubric=rubric,
            transcript=transcript_text,
            pdf_data=pdf_content,
            teacher_id=current_user.id
        )
        db.add(report)
        db.commit()

        return jsonify({"message": "Report generated", "report_id": uid})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure temp files are cleaned up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ============================================================
# 5️⃣ Main
# ============================================================
if __name__ == "__main__":
    # Check if tables exist, if not, create them
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)