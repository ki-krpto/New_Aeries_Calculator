import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database file path
DB_FILE = 'grades.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Classes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            class_name TEXT NOT NULL,
            teacher_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Categories table (Classwork, Labs, Tests & Quizzes, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE
        )
    ''')
    
    # Assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            points_earned REAL,
            points_possible REAL NOT NULL,
            comment TEXT,
            date_completed TEXT,
            due_date TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def create_demo_user():
    """Create a demo user for testing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if demo user exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
        if cursor.fetchone() is None:
            # Create demo user with password 'demo'
            hashed_password = generate_password_hash('demo')
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         ('demo', hashed_password))
            conn.commit()
            print("Demo user created! Username: demo, Password: demo")
    except Exception as e:
        print(f"Error creating demo user: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    create_demo_user()
