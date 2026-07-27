import sqlite3 as sql
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'gym.db')

def get_connection():
    conn = sql.connect(DATABASE_PATH)
    conn.row_factory = sql.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def user_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Insert default admin
def insert_default_admin():
    conn = get_connection()
    cur = conn.cursor()

    # admin already exists ka check
    cur.execute("SELECT * FROM users WHERE email=?", ('admin@gym.com',))
    admin = cur.fetchone()

    if admin is None:
        cur.execute(
            "INSERT INTO users(name, email, mobile, password, role) VALUES(?,?,?,?,?)",
            ('admin', 'admin@gym.com', '9999999999', 'admin123', 'admin')
        )
        conn.commit()
        print("Default admin inserted")
    else:
        print("Admin already exists")

    conn.close()

# Members table
def create_members_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS members(
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            height REAL,
            weight REAL,
            address TEXT,
            joining_date TEXT DEFAULT (DATE('now')),
            status TEXT DEFAULT 'Active'
        )
    ''')

    conn.commit()
    conn.close()
    print("Members table created")

def create_membership_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS membership_plan(
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT NOT NULL,
            duration INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def create_member_membership_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS member_membership(
            membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date DATE DEFAULT CURRENT_DATE,
            end_date DATE,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY(member_id) REFERENCES members(member_id),
            FOREIGN KEY(plan_id) REFERENCES membership_plan(plan_id)

        )
    ''')

    conn.commit()
    conn.close()

def create_payments_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments(

        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,

        member_id INTEGER NOT NULL,

        amount REAL NOT NULL,

        payment_date DATE DEFAULT CURRENT_DATE,

        payment_mode TEXT NOT NULL,

        remarks TEXT,

        FOREIGN KEY(member_id)
        REFERENCES members(member_id)

    )
    """)

    conn.commit()
    conn.close()

def create_attendance_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(

            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,

            member_id INTEGER NOT NULL,

            attendance_date DATE DEFAULT CURRENT_DATE,

            check_in_time TEXT,

            status TEXT DEFAULT 'Present',

            FOREIGN KEY(member_id)
            REFERENCES members(member_id)

        )
    """)

    conn.commit()
    conn.close()

    print("Attendance table created")


def create_attendance_table():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(

            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,

            member_id INTEGER NOT NULL,

            attendance_date DATE DEFAULT CURRENT_DATE,

            attendance_time TIME DEFAULT CURRENT_TIME,

            latitude REAL,

            longitude REAL,

            status TEXT DEFAULT 'Present',

            FOREIGN KEY(member_id)
            REFERENCES members(member_id)

        )
    """)

    conn.commit()
    conn.close()

    print("Attendance table created")