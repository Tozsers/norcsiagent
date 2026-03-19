import sqlite3
import json
from datetime import datetime

DB_PATH = "sasagent.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'idle',
            last_seen TEXT,
            meta TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT,
            data TEXT DEFAULT '{}',
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            command TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def upsert_agent(agent_id, name, status, meta=None):
    conn = get_db()
    conn.execute("""
        INSERT INTO agents (id, name, status, last_seen, meta)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            status=excluded.status,
            last_seen=excluded.last_seen,
            meta=excluded.meta
    """, (agent_id, name, status, datetime.now().isoformat(), json.dumps(meta or {})))
    conn.commit()
    conn.close()

def add_event(agent_id, event_type, message, data=None):
    conn = get_db()
    conn.execute("""
        INSERT INTO events (agent_id, event_type, message, data, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (agent_id, event_type, message, json.dumps(data or {}), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_agents():
    conn = get_db()
    rows = conn.execute("SELECT * FROM agents ORDER BY last_seen DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_agent_events(agent_id, limit=50):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM events WHERE agent_id = ?
        ORDER BY timestamp DESC LIMIT ?
    """, (agent_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_command(agent_id, command):
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO commands (agent_id, command, timestamp)
        VALUES (?, ?, ?)
    """, (agent_id, command, datetime.now().isoformat()))
    conn.commit()
    cmd_id = cur.lastrowid
    conn.close()
    return cmd_id

def get_pending_commands(agent_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM commands WHERE agent_id = ? AND status = 'pending'
        ORDER BY timestamp ASC
    """, (agent_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_command_done(cmd_id):
    conn = get_db()
    conn.execute("UPDATE commands SET status='done' WHERE id=?", (cmd_id,))
    conn.commit()
    conn.close()
