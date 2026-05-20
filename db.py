import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "dockmate.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            context TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tools_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def create_project(name: str, context: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO projects (name, context) VALUES (?, ?)', (name, context))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_project(project_id)

def get_project(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_messages(project_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages WHERE project_id = ? ORDER BY created_at ASC', (project_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def add_message(project_id: int, role: str, content: str, tools_used: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO messages (project_id, role, content, tools_used) VALUES (?, ?, ?, ?)',
        (project_id, role, content, tools_used)
    )
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id
