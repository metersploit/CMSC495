# Class Registration System

The code is written in Python and uses a SQLite database. It is organized into
layers, and a request flows through them in order:

```
ui  ->  validator  ->  service  ->  dao  ->  db
```

with `models` as the plain data objects passed between the layers.

## Project layout

```
registration-system/
├── models/      data objects shared across layers
├── db/          database connection + schema builder
├── dao/         data-access layer (CRUD)
├── service/     backend business logic
├── validator/   input-validation middleware
└── ui/          front-end screens
```

## models/

Plain data classes (Python `dataclass`es) that mirror the database tables and
are passed between layers: `Student`, `Course` (with a `has_available_seats`
helper), and `Enrollment`. They hold data only.

## db/

`DatabaseConnection` is a  wrapper around a single SQLite connection;
it sets `row_factory` so rows can be read by column name and turns on foreign-key
enforcement on every connection. `build_db.py` creates the `students`,
`courses`, and `enrollment` tables, including a default seat count
(`num_enrolled NOT NULL DEFAULT 0`) and a `UNIQUE(student_id, course_id)`
constraint so a student can't enroll in the same course twice. Run it once
before first use. The path is anchored to this folder, so the builder and the
connection always use the same database file.

## dao/

The data-access layer. `DataAccessObject` is the generic interface
(`insert_row`, `find_row`, `update_row`, `delete_row`). `BaseDAO` implements that
contract a single time using small per-table hooks (table name, columns,
object/row mapping), so `StudentDAO`, `CourseDAO`, and `EnrollmentDAO` only add
their table specifics plus a few specialized queries—`find_by_email` (login),
`search` (course lookup), and `find_by_student` / `find_active` (schedule and
drop). DAO write methods execute SQL but do not commit; the service owns the
transaction boundary.

## service/

`BackendController` is the backend that the front end ultimately calls. It
applies various rules (course-capacity check, duplicate-enrollment guard),
hashes and verifies passwords, and wraps multi-step writes such as enroll and
drop in a transaction so the seat count can't doesn't. Operations that fail (course full, already enrolled, bad credentials) raise
`RegistrationError`.

## validator/

`Validator` is the middleware between the UI and the backend. It checks that
input is complete and well formed, rejects bad input with a per-field
`ValidationError` (so invalid data never reaches the database), and forwards
valid requests to `BackendController`. This is the layer that realizes the
project's frontend-to-backend validation requirement.

## ui/

The front-end screens. `View` is the abstract base for every screen: it holds
the `Validator` and the logged-in student, declares the framework-specific
methods each screen must implement (`render`, `show_error`, `show_message`), and
provides the shared `report_validation_error` loop that displays every field
error at once. The concrete screens (`LoginView`, `CreateAccountView`,
`SearchCoursesView`, `AddDropCoursesView`, `ScheduleView`) and the
`UserInterface` that displays them build on `View`. The GUI framework has not
been chosen yet, so `View` is framework-neutral.

## Errors

Two exception types flow back to the UI:

- `ValidationError` (from `validator/`) — field-level input problems; carries a
  `field → message` map so each input can be flagged.
- `RegistrationError` (from `service/`) — business problems such as a full
  course or duplicate enrollment.

## Running

1. Build the database once: `python3 db/build_db.py`
2. Nothing else because it hasn't been implemented yet.