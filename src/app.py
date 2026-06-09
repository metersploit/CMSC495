# Filename: app.py
#
# Description: This is the entry point for the program and serves as the program's
# front end. It builds a Flask app for app use in a web browser. Run the script,
# and go to http://127.0.0.1:5000 to acccess the app in your browser.
#
# Parent: None

from functools import wraps

from flask import (Flask, g, request, session, redirect, url_for,
                   render_template, flash)

from db.database_connection import DatabaseConnection
from service.backend_controller import BackendController, RegistrationError
from validator import Validator, ValidationError

app = Flask(__name__)

# This line wouldn't exist in a prod app and would be considered sensitive, so
# it would live as an env var and not in the repo. This is non-prod and with
# no sensitive data to protect so its fine.
app.secret_key = "c76699dc-c1d3-493c-9388-9714df3654a4"


def get_validator() -> Validator:
    if "validator" not in g:
        g.db = DatabaseConnection()
        g.validator = Validator(BackendController(g.db))
    return g.validator


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def _first_message(error) -> str:
    if isinstance(error, ValidationError):
        return next(iter(error.errors.values()), "Invalid input.")
    return str(error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            get_validator().create_account(
                request.form.get("first_name"),
                request.form.get("last_name"),
                request.form.get("email"),
                request.form.get("phone_number"),
                request.form.get("password"),
            )
            flash("Account created — please log in.")
            return redirect(url_for("login"))
        except ValidationError as e:
            return render_template("register.html", errors=e.errors, form=request.form)
        except RegistrationError as e:
            return render_template("register.html", errors={"email": str(e)}, form=request.form)
    return render_template("register.html", errors={}, form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            student = get_validator().login(
                request.form.get("email"),
                request.form.get("password"),
            )
            session["student_id"] = student.student_id
            session["name"] = student.first_name
            return redirect(url_for("schedule"))
        except ValidationError as e:
            return render_template("login.html", errors=e.errors, form=request.form)
        except RegistrationError as e:
            return render_template("login.html", errors={"password": str(e)}, form=request.form)
    return render_template("login.html", errors={}, form={})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/courses")
@login_required
def courses():
    term = request.args.get("q", "")
    results = []
    if term:
        try:
            results = get_validator().search_courses(term)
        except ValidationError as e:
            flash(_first_message(e))
    return render_template("courses.html", courses=results, term=term)


@app.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    try:
        get_validator().enroll(session["student_id"], course_id)
        flash("Enrolled.")
    except (ValidationError, RegistrationError) as e:
        flash(_first_message(e))
    return redirect(request.referrer or url_for("courses"))


@app.route("/drop/<int:course_id>", methods=["POST"])
@login_required
def drop(course_id):
    try:
        get_validator().drop(session["student_id"], course_id)
        flash("Dropped.")
    except (ValidationError, RegistrationError) as e:
        flash(_first_message(e))
    return redirect(url_for("schedule"))


@app.route("/")
@app.route("/schedule")
@login_required
def schedule():
    courses = get_validator().get_schedule(session["student_id"])
    return render_template("schedule.html", courses=courses)


if __name__ == "__main__":
    app.run(debug=True)