from flask import Flask, redirect, url_for, session, flash
from app.blueprints import mission_bp, config_bp, forms_bp, submission_bp, huey_bp
from contactform.mission import create_tables

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = (
    "your-secret-key-here"  # Change this in production pragma: allowlist secret
)

# Initialize database tables
try:
    create_tables()
except Exception as e:
    print(f"Warning: Could not initialize database tables: {e}")

# Register blueprints
app.register_blueprint(mission_bp)
app.register_blueprint(config_bp)
app.register_blueprint(forms_bp)
app.register_blueprint(submission_bp)
app.register_blueprint(huey_bp)


@app.route("/")
def index():
    """Redirect to mission list"""
    return redirect(url_for("mission.mission_list"))


@app.route("/reset_session")
def reset_session():
    """Reset session and go back to mission list"""
    session.clear()
    flash("Session reset. Please start over.", "info")
    return redirect(url_for("mission.mission_list"))


if __name__ == "__main__":
    app.run(debug=True)
