# Class Registration System

A student course-registration for CMSC 495.
Students can create an account, log in, search for classes, add and drop
classes, and view their schedule. Every user submission is validated before it
reaches the database..

The code is written in Python and uses a SQLite database with a Flask web front
end. It is organized into layers, and a request flows through them in order:

```
browser  ->  Flask (app.py)  ->  validator  ->  service  ->  dao  ->  db
```

with `models` as the plain data objects passed between the layers.

## Project layout

```
src/                    (project root — run all commands from here)
├── app.py              Flask routes (the web UI)
├── seed.py             inserts sample courses + a test student
├── requirements.txt    Python dependencies (Flask)
├── templates/          HTML pages rendered by Flask
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   ├── courses.html
│   └── schedule.html
├── models/             data objects shared across layers
├── db/                 database connection, schema builder, the .db file
├── dao/                data-access layer (CRUD)
├── service/            backend business logic
├── validator/          input-validation middleware
└── ui/                 abstract View (desktop UI — NOT used by the web app)
```

## Web layer (app.py + templates/)

The Flask app is the front end. Each route (`/register`, `/login`, `/logout`,
`/courses`, `/enroll/<id>`, `/drop/<id>`, `/schedule`) handles a request by
calling the matching `Validator` method and rendering an HTML template. Login
state is kept in the Flask session, and a fresh database connection is opened
per request (SQLite connections can't be shared across the server's threads).
Pages use semantic HTML styled by Pico.css from a CDN, so they look clean with
no custom CSS.

## models/

Plain data classes (Python `dataclass`es) that mirror the database tables and
are passed between layers: `Student`, `Course` (with a `has_available_seats`
helper), and `Enrollment`. Data only — no database or UI logic.

## db/

`DatabaseConnection` is a singleton wrapper around a SQLite connection; it sets
`row_factory` so rows read by column name and enables foreign-key enforcement on
every connection. `build_db.py` creates the `students`, `courses`, and
`enrollment` tables, including `num_enrolled NOT NULL DEFAULT 0` and a
`UNIQUE(student_id, course_id)` constraint so a student can't enroll in the same
course twice. The database file `registration_app.db` lives in this folder, and
the path is anchored to the folder so the builder and the app always use the
same file.

## dao/

The data-access layer. `DataAccessObject` is the generic CRUD interface.
`BaseDAO` implements it once using per-table hooks, so `StudentDAO`,
`CourseDAO`, and `EnrollmentDAO` only add their table specifics plus specialized
queries (`find_by_email`, `search`, `find_by_student`, `find_active`). DAO write
methods execute SQL but do **not** commit; the service owns the transaction.

## service/

`BackendController` is the backend facade. It applies the business rules
(capacity check, duplicate-enrollment guard), hashes and verifies passwords, and
wraps enroll/drop in a transaction so the seat count can't drift. Business
failures (course full, already enrolled, bad credentials) raise
`RegistrationError`.

## validator/

`Validator` is the middleware between the web layer and the backend. It checks
that input is complete and well formed, rejects bad input with a per-field
`ValidationError` (so invalid data never reaches the database), and forwards
valid requests to `BackendController`.

## ui/

`View` is an abstract base for a desktop (Tkinter) UI. It is **not used by the
Flask web app** and is kept only in case a desktop build is added later. Because
the backend is decoupled, a desktop UI and the web app could share the same
`service`/`dao`/`db` code.

## Errors

Two exception types flow back to the front end:

- `ValidationError` (from `validator/`) — field-level input problems; carries a
  `field -> message` map so each input can be flagged.
- `RegistrationError` (from `service/`) — business problems such as a full
  course or duplicate enrollment.

## Running

Run everything from the project root (`src/`) so the package imports resolve:

1. Install dependencies: `pip install -r requirements.txt`
2. Build the database (once): `python3 db/build_db.py`
3. Add sample data: `python3 seed.py`
4. Start the app: `python3 app.py`
5. Open `http://127.0.0.1:5000` and log in with the seeded test account:
   `test@umgc.edu` / `password123`

Notes:

- Re-running `seed.py` is safe — it skips courses if any already exist and skips
  the test student if the email is taken.
- To reset to a clean state, delete `db/registration_app.db` and repeat steps
  2-3.
- If port 5000 is in use (on macOS, AirPlay uses it), change the last line of
  `app.py` to `app.run(debug=True, port=5001)` and open that port instead.
- The `secret_key` in `app.py` signs the login session cookie. Use a real random
  value and keep it out of version control (environment variable or an ignored
  config file).