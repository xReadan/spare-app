import sqlite3
import os.path


def connect_to_db():
    # Check if database exist
    db_path = "./data.db"
    if not os.path.isfile(db_path):
        conn = create_db()
    else:
        conn = sqlite3.connect("data.db")
    return conn, conn.cursor()


def create_db():
    conn = sqlite3.connect("data.db")
    # Setup tables
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            username TEXT,
            password TEXT)"""
    )
    cursor.execute(
        """CREATE TABLE categories (
            id INTEGER PRIMARY KEY, 
            name TEXT,
            threshold INTEGER,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) 
            ON DELETE CASCADE)"""
    )
    cursor.execute(
        """CREATE TABLE incomes (
            id INTEGER PRIMARY KEY, 
            income REAL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) 
            ON DELETE CASCADE)"""
    )
    cursor.execute(
        """CREATE TABLE expenses (
            id INTEGER PRIMARY KEY, 
            date TEXT,
            amount REAL,
            user_id INTEGER,
            recurring INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) 
            ON DELETE CASCADE)"""
    )

    return conn
