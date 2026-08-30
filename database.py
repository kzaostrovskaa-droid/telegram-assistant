import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            deadline TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            remind_at TEXT,
            sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_task(user_id, title, description="", deadline=None):
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (user_id, title, description, deadline, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, description, deadline, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_tasks(user_id):
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    cur.execute("SELECT id, title, deadline, status FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_reminder(user_id, text, remind_at):
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (user_id, text, remind_at) VALUES (?, ?, ?)",
        (user_id, text, remind_at)
    )
    conn.commit()
    conn.close()

def get_pending_reminders():
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("SELECT id, user_id, text FROM reminders WHERE remind_at <= ? AND sent = 0", (now,))
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_reminder_sent(reminder_id):
    conn = sqlite3.connect("assistant.db")
    cur = conn.cursor()
    cur.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()