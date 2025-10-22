from functools import wraps
from flask import request, jsonify

def require_auth(f):
    '''Require user authentication'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def require_admin_auth(f):
    '''Require admin-level authentication'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401

        user = get_user_from_token(token)
        if not user.is_admin:
            return jsonify({'error': 'Forbidden - Admin only'}), 403

        return f(*args, **kwargs)
    return decorated

def verify_token(token):
    '''Verify JWT token (stub for testing)'''
    # Implementation would go here
    return True

def get_user_from_token(token):
    '''Extract user from JWT token (stub for testing)'''
    # Implementation would go here
    class User:
        is_admin = False
    return User()
