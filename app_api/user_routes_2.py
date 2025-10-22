from flask import Flask, request, jsonify, send_file
from db import get_db_connection
from auth import require_admin_auth, require_auth
from sanitizers import html_sanitizer, path_sanitizer

app = Flask(__name__)

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    '''Get user profile by ID'''
    conn = get_db_connection()
    cursor = conn.cursor()

    # Secure: Using parameterized query
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

    # Secure: Input sanitization
    safe_query = html_sanitizer.clean(query)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username LIKE %s", (f'%{safe_query}%',))
    results = cursor.fetchall()

    return jsonify([{'id': r[0], 'username': r[1]} for r in results])

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin_auth
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

    # Secure: Path sanitization to prevent traversal
    safe_path = path_sanitizer.clean(filename)

    return send_file(f'/var/avatars/{safe_path}')
