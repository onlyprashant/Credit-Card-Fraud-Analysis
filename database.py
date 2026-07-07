import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "users.db"


# ============================================================
# Create Database & Users Table
# ============================================================

def initialize_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            college TEXT,

            department TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


# ============================================================
# Register User
# ============================================================

def register_user(full_name,
                  email,
                  password,
                  college,
                  department):

    try:

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute("""

            INSERT INTO users(

                full_name,
                email,
                password,
                college,
                department

            )

            VALUES(?,?,?,?,?)

        """, (

            full_name,
            email,
            hashed_password,
            college,
            department

        ))

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:

        return False


# ============================================================
# Authenticate User
# ============================================================

def authenticate_user(email, password):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE email=?

    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    if check_password_hash(user[3], password):
        return user

    return None


# ============================================================
# Get User Profile
# ============================================================

def get_user(user_id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE id=?

    """, (user_id,))

    user = cursor.fetchone()

    conn.close()

    return user


# ============================================================
# Run Directly
# ============================================================

if __name__ == "__main__":

    initialize_database()