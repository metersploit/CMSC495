If you're the Summer 2026 CMSC 495 instructor, scroll down to "Class Registration System" to see the main part of the readme. 

If you're in group 4, the notes between here and "Class Registration System" are for you.

The main branch can't be pushed to directly, so you'll need to checkout a branch
first, make your changes, push the branch, and then open a PR.

```
git clone https://github.com/metersploit/CMSC495.git
cd CMSC495/
git checkout -b your-branch-name-here
```

Make your changes. When you're ready to push:

```
cd path/to/CSMSC495/
git add .
git commit -m "Write your commit message here"
git push -u origin your-branch-name-here
```
Then go to Pull Requests on Github (this repo) and open a PR. 

If you have set up a signing key, add `-S` to your commit command. It isn't a 
requirement for this repo, but it is very common to see in other repos, so its
worth learning how to do.

If you already have a local copy somewhere and want to work off of that instead of
cloning every time:

```
cd path/to/CMSC495/
git checkout main
git pull
git checkout -b your-branch-name-here
```
You might already be on the main branch and/or have an up-to-date copy of the repo. If thats the case, the commands immediately above here are still safe to run, and git will report that one or both are already true.

CI/CD TODOs (if I have time)
```
- PR templates
- Linter
- Runner for automated testing
- Enforce automated testing
- Smoke checks
```

# Class Registration System

A student course-registration application for group 4 of CMSC 495.
Students can create an account, log in, search for classes, add and drop
classes, and view their schedule. Every user submission is validated before it
reaches the database, which is the project's main focus.

The code is written in Python and uses a SQLite database with a Flask web front
end. It is organized into layers, and a request flows through them in order:

```
browser  ->  Flask (app.py)  ->  validator  ->  service  ->  dao  ->  db
```

with `models` as the plain data objects passed between the layers.

## Project layout

```
src/                    project root
├── setup_app.py        one-command setup + run
├── app.py              Flask routes
├── seed.py             inserts sample courses + a test student
├── requirements.txt    Python dependencies (Flask)
├── templates/          HTML pages rendered by Flask
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   ├── courses.html
│   └── schedule.html
├── models/             data objects shared across layers
├── db/                 db connection, schema builder, the .db file
├── dao/                data-access layer
├── service/            backend logic
├── validator/          input validation
└── ui/                 abstract View (not in use)
```

## Web layer (app.py + templates/)

The Flask app is the front end. Each route (`/register`, `/login`, `/logout`,
`/courses`, `/enroll/<id>`, `/drop/<id>`, `/schedule`) handles a request by
calling the matching `Validator` method and rendering an HTML template. Login
state is kept in the Flask session, and a fresh database connection is opened
per request. Pages use HTML styled by Pico.css from a CDN, so no custom CSS.

## models/

Data classes (Python `dataclass`es) that mirror the database tables and
are passed between layers: `Student`, `Course` (with a `has_available_seats`
helper), and `Enrollment`. Data only.

## db/

`DatabaseConnection` is a wrapper around a SQLite connection. It sets
`row_factory` so rows read by column name and enables foreign-key enforcement on
every connection. `build_db.py` creates the `students`, `courses`, and
`enrollment` tables, including `num_enrolled NOT NULL DEFAULT 0` and a
`UNIQUE(student_id, course_id)` constraint so a student can't enroll in the same
course twice. The database file `registration_app.db` lives in this folder, and
the path is anchored to the folder so the builder and the app always use the
same file.

## dao/

The data-access layer. `DataAccessObject` is the generic interface.
`BaseDAO` implements it once using per-table hooks, so `StudentDAO`,
`CourseDAO`, and `EnrollmentDAO` only add their table specifics plus specialized
queries (`find_by_email`, `search`, `find_by_student`, `find_active`). DAO write
methods execute SQL but do don't commit. Instead, the service owns the connection.

## service/

`BackendController` is the backend facade. It applies the rules
(capacity check, duplicate-enrollment guard), hashes and verifies passwords, and
wraps enroll/drop in a transaction so the seat count can't drift. Failures
(course full, already enrolled, bad credentials) raise `RegistrationError`.

## validator/

`Validator` is the middleware between the web layer and the backend. It checks
that input is complete and well formed, rejects bad input with a per-field
`ValidationError` (so invalid data never reaches the database), and forwards
valid requests to `BackendController`.

## ui/

Currently not in use.

## Errors

Two exception types flow back to the front end:

- `ValidationError` (from `validator/`) — field-level input problems; carries a
  `field -> message` map so each input can be flagged.
- `RegistrationError` (from `service/`) — problems such as a full
  course or duplicate enrollment.

## Running

The easiest way is the setup script. From the project root (`src/`), run it with
your system Python. It creates a virtual environment, installs dependencies,
builds and seeds the database, and starts the app:

```
python3 setup_app.py          # macOS / Linux
python setup_app.py           # Windows
```

Then open `http://127.0.0.1:5000` and log in with the seeded test account:
`test@umgc.edu` / `password123`. You can optionally create a new account. 
Press Ctrl+C to stop the server. The script is safe to re-run, so it doubles as
the everyday "start the app" command.

### Manual steps

If you'd rather run each step yourself from the project root:

1. Install dependencies: `pip install -r requirements.txt`
2. Build the database: `python3 db/build_db.py`
3. Add sample data: `python3 seed.py`
4. Start the app: `python3 app.py`

### Notes

- Re-running `seed.py` (or `setup_app.py`) is safe since it skips courses if any
  already exist and skips the test student if the email is taken.
- To reset to a clean state, delete `db/registration_app.db` and run
  `setup_app.py` again or repeat the manual build/seed steps.
- If port 5000 is in use (on macOS, AirPlay uses it), change the last line of
  `app.py` to `app.run(debug=True, port=5001)` and open that port instead.
