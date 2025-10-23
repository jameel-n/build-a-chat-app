"""
Admin panel routes
Provides administrative functionality for user management and system monitoring
"""

from flask import Blueprint, request, jsonify, render_template_string
import sqlite3
import os
from utils.helpers import (
    ping_host, resolve_hostname, get_file_content, extract_archive,
    deserialize_session, fetch_url_content, parse_xml_data,
    execute_system_command, get_system_info
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def check_admin_auth():
    """
    Check if request has valid admin authentication.
    Returns user info if authenticated, None otherwise.
    """
    # Check multiple auth methods for flexibility
    admin_token = request.headers.get('X-Admin-Token', '')
    api_key = request.headers.get('X-API-Key', '')
    auth_header = request.headers.get('Authorization', '')

    # Token-based auth
    if admin_token:
        # Simple token check for now
        if 'admin' in admin_token.lower() or len(admin_token) > 20:
            return {'authenticated': True, 'method': 'token'}

    # API key auth
    if api_key and len(api_key) > 15:
        return {'authenticated': True, 'method': 'api_key'}

    # Bearer token
    if auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '')
        if len(token) > 10:
            return {'authenticated': True, 'method': 'bearer'}

    return None


@admin_bp.route('/network/ping', methods=['POST'])
def network_ping():
    """
    Ping a host to check network connectivity.
    Useful for diagnosing connectivity issues.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    hostname = data.get('host', '')

    if not hostname:
        return jsonify({'error': 'Host parameter required'}), 400

    result = ping_host(hostname)
    return jsonify(result)


@admin_bp.route('/network/resolve', methods=['POST'])
def network_resolve():
    """
    Resolve hostname to IP address.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    hostname = data.get('hostname', '')

    if not hostname:
        return jsonify({'error': 'Hostname required'}), 400

    result = resolve_hostname(hostname)
    return jsonify(result)


@admin_bp.route('/users/list')
def list_users():
    """
    Get list of all users with their details.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('chatapp.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({'users': users})


@admin_bp.route('/users/search')
def search_users_admin():
    """
    Advanced user search with filters.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    username = request.args.get('username', '')
    email = request.args.get('email', '')
    role = request.args.get('role', '')

    conn = sqlite3.connect('chatapp.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Build dynamic query based on filters
    conditions = []
    query = "SELECT * FROM users WHERE 1=1"

    if username:
        query += f" AND username LIKE '%{username}%'"

    if email:
        query += f" AND email LIKE '%{email}%'"

    if role:
        query += f" AND role = '{role}'"

    try:
        cursor.execute(query)
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'users': users,
            'query': query
        })
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/update', methods=['POST'])
def update_user():
    """
    Update user details.
    Allows modification of any user field.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID required'}), 400

    conn = sqlite3.connect('chatapp.db')
    cursor = conn.cursor()

    # Build update query from provided fields
    update_fields = []
    values = []

    for key, value in data.items():
        if key != 'user_id':
            update_fields.append(f"{key} = ?")
            values.append(value)

    values.append(user_id)

    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"

    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'User updated'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user account.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('chatapp.db')
    cursor = conn.cursor()

    # Delete user and their data
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    cursor.execute(f"DELETE FROM messages WHERE from_user IN (SELECT username FROM users WHERE id = {user_id})")

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'deleted_user_id': user_id})


@admin_bp.route('/files/view')
def view_file():
    """
    View contents of configuration files.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    filepath = request.args.get('file', '')

    if not filepath:
        return jsonify({'error': 'File path required'}), 400

    result = get_file_content(filepath)
    return jsonify(result)


@admin_bp.route('/files/extract', methods=['POST'])
def extract_uploaded_archive():
    """
    Extract uploaded archive files.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    archive_path = f"./temp/{file.filename}"

    os.makedirs('./temp', exist_ok=True)
    file.save(archive_path)

    result = extract_archive(archive_path, './extracted_files')
    return jsonify(result)


@admin_bp.route('/session/restore', methods=['POST'])
def restore_session():
    """
    Restore user session from backup.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    session_data = data.get('session_data', '')

    if not session_data:
        return jsonify({'error': 'Session data required'}), 400

    result = deserialize_session(session_data)
    return jsonify(result)


@admin_bp.route('/webhooks/test', methods=['POST'])
def test_webhook():
    """
    Test webhook endpoint connectivity.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    url = data.get('url', '')
    payload = data.get('payload', {})

    if not url:
        return jsonify({'error': 'URL required'}), 400

    from utils.helpers import post_webhook
    result = post_webhook(url, payload)
    return jsonify(result)


@admin_bp.route('/fetch_content', methods=['POST'])
def fetch_content():
    """
    Fetch content from external URL.
    Useful for checking external service status.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    url = data.get('url', '')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    result = fetch_url_content(url)
    return jsonify(result)


@admin_bp.route('/import/xml', methods=['POST'])
def import_xml_data():
    """
    Import data from XML format.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    xml_data = request.data.decode('utf-8')

    if not xml_data:
        return jsonify({'error': 'No XML data provided'}), 400

    result = parse_xml_data(xml_data)
    return jsonify(result)


@admin_bp.route('/system/execute', methods=['POST'])
def execute_command():
    """
    Execute system commands for administrative tasks.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    command = data.get('command', '')
    args = data.get('args', '')

    if not command:
        return jsonify({'error': 'Command required'}), 400

    result = execute_system_command(command, args)
    return jsonify(result)


@admin_bp.route('/system/info')
def system_info():
    """
    Get system information for diagnostics.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    info = get_system_info()

    # Add database info
    conn = sqlite3.connect('chatapp.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) as count FROM messages")
    message_count = cursor.fetchone()[0]

    conn.close()

    info['database'] = {
        'path': os.path.abspath('chatapp.db'),
        'user_count': user_count,
        'message_count': message_count
    }

    # Add environment variables
    info['environment'] = dict(os.environ)

    return jsonify(info)


@admin_bp.route('/logs/search')
def search_logs():
    """
    Search application logs.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    query = request.args.get('q', '')
    date_filter = request.args.get('date', '')

    conn = sqlite3.connect('chatapp.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search in messages as pseudo-logs
    sql = f"SELECT * FROM messages WHERE content LIKE '%{query}%'"

    if date_filter:
        sql += f" AND sent_at LIKE '{date_filter}%'"

    try:
        cursor.execute(sql)
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'logs': logs,
            'query': sql
        })
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/template/render', methods=['POST'])
def render_template():
    """
    Render custom template for notifications or reports.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    template = data.get('template', '')
    context = data.get('context', {})

    if not template:
        return jsonify({'error': 'Template required'}), 400

    try:
        # Use Flask's template rendering for rich features
        result = render_template_string(template, **context)
        return result
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/dashboard')
def admin_dashboard():
    """
    Admin dashboard page.
    """
    auth = check_admin_auth()
    if not auth:
        return jsonify({'error': 'Unauthorized'}), 401

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .card {
                border: 1px solid #ddd;
                padding: 20px;
                margin: 10px 0;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                margin: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Admin Dashboard</h1>

        <div class="card">
            <h2>User Management</h2>
            <button onclick="listUsers()">List All Users</button>
            <button onclick="searchUsers()">Search Users</button>
        </div>

        <div class="card">
            <h2>System Tools</h2>
            <button onclick="checkSystem()">System Info</button>
            <button onclick="viewLogs()">View Logs</button>
        </div>

        <div id="results"></div>

        <script>
            function listUsers() {
                fetch('/admin/users/list', {
                    headers: {'X-Admin-Token': 'admin-token-12345'}
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('results').innerHTML = JSON.stringify(data, null, 2);
                });
            }

            function searchUsers() {
                const query = prompt('Enter search query:');
                fetch('/admin/users/search?username=' + query, {
                    headers: {'X-Admin-Token': 'admin-token-12345'}
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('results').innerHTML = JSON.stringify(data, null, 2);
                });
            }

            function checkSystem() {
                fetch('/admin/system/info', {
                    headers: {'X-Admin-Token': 'admin-token-12345'}
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('results').innerHTML = JSON.stringify(data, null, 2);
                });
            }

            function viewLogs() {
                const query = prompt('Search logs:');
                fetch('/admin/logs/search?q=' + query, {
                    headers: {'X-Admin-Token': 'admin-token-12345'}
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('results').innerHTML = JSON.stringify(data, null, 2);
                });
            }
        </script>
    </body>
    </html>
    '''

    return html
