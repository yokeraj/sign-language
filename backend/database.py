import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "school.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL,
            roll_no TEXT    UNIQUE NOT NULL,
            class   TEXT,
            section TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject    TEXT,
            marks      REAL,
            max_marks  REAL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()

# ── Student queries ──────────────────────────────────────
def insert_student(name, roll_no, cls, section):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, roll_no, class, section) VALUES (?,?,?,?)",
        (name, roll_no, cls, section)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def fetch_all_students():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT id, name, roll_no, class, section FROM students")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_student(student_id):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT id, name, roll_no, class, section FROM students WHERE id=?", (student_id,))
    row = cur.fetchone()
    conn.close()
    return row

# ── Marks queries ────────────────────────────────────────
def insert_marks(student_id, subjects):
    conn = get_conn()
    cur  = conn.cursor()
    for s in subjects:
        cur.execute(
            "INSERT INTO marks (student_id, subject, marks, max_marks) VALUES (?,?,?,?)",
            (student_id, s["subject"], s["marks"], s["max_marks"])
        )
    conn.commit()
    conn.close()

def fetch_marks(student_id):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(
        "SELECT subject, marks, max_marks FROM marks WHERE student_id=?",
        (student_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows