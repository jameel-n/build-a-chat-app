# VULNERABLE VERSION - Use this to replace user_routes.py in your PR
# This file contains INTENTIONAL security vulnerabilities for testing

from flask import Flask, request, jsonify, send_file
from db import get_db_connection
from auth import require_auth  # REMOVED require_admin_auth import
from sanitizers import html_sanitizer  # REMOVED path_sanitizer import

app = Flask(__name__)

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    '''Get user profile by ID'''
    conn = get_db_connection()
    cursor = conn.cursor()

    # Secure: Using parameterized query (unchanged)
    cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user[0],
        'username': user[1],
        'email': user[2]
    })

@app.route('/api/users/search', methods=['GET'])
@require_auth
def search_users():
    '''Search users by username'''
    query = request.args.get('q', '')

    # VULNERABILITY 1: SQL Injection - String concatenation instead of parameterized query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, username FROM users WHERE username LIKE '%{query}%'")
    results = cursor.fetchall()

    return jsonify([{'id': r[0], 'username': r[1]} for r in results])

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
# VULNERABILITY 2: Authorization Bypass - Removed @require_admin_auth decorator
@require_auth  # Only basic auth, not admin!
def delete_user(user_id):
    '''Admin endpoint to delete users'''
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    return jsonify({'message': 'User deleted'}), 200

@app.route('/api/profile/avatar', methods=['GET'])
@require_auth
def get_avatar():
    '''Serve user avatar files'''
    filename = request.args.get('file', 'default.png')

    # VULNERABILITY 3: Path Traversal - Direct file access without sanitization
    return send_file(f'/var/avatars/{filename}')

@app.route('/api/admin/debug', methods=['GET'])
@require_auth  # VULNERABILITY 4: New admin endpoint without admin auth
def admin_debug():
    '''Debug endpoint for viewing system info'''
    import os

    # VULNERABILITY 5: Command Injection
    system_info = os.popen(f"uname -a && whoami").read()

    return jsonify({'system_info': system_info})
