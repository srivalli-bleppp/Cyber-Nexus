import sqlite3

DATABASE = "cyber_investigation.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Security events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT,
            timestamp TEXT,
            source TEXT,
            host TEXT,
            event_type TEXT,
            src_ip TEXT,
            message TEXT,
            process TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            risk_score INTEGER,
            severity TEXT,
            status TEXT
        )
    """)

    # Demo users
    demo_users = [
        ("U001", "arjun", "employee", "active"),
        ("U002", "rahul", "employee", "active"),
        ("U003", "priya", "employee", "active"),
        ("A001", "admin", "security_admin", "active")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO users
        (user_id, username, role, status)
        VALUES (?, ?, ?, ?)
    """, demo_users)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")