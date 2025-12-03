import os
import hashlib
import re
from werkzeug.utils import secure_filename

UPLOAD_DIR = '/var/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    '''Check if file extension is allowed'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_safe_filename(original_filename, user_id):
    '''Generate a safe filename based on user ID and original name'''
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    base = hashlib.md5(f"{user_id}_{original_filename}".encode()).hexdigest()[:12]
    return f"{base}.{ext}"

def save_user_avatar(file_data, user_id, filename):
    '''Save user avatar to disk'''
    if not allowed_file(filename):
        raise ValueError("Invalid file type")

    safe_name = generate_safe_filename(filename, user_id)
    avatar_path = os.path.join(UPLOAD_DIR, 'avatars', str(user_id), safe_name)

    os.makedirs(os.path.dirname(avatar_path), exist_ok=True)

    with open(avatar_path, 'wb') as f:
        f.write(file_data)

    return avatar_path

def save_chat_attachment(file_data, room_id, filename, subdirectory=None):
    '''Save chat attachment for a room.

    Args:
        file_data: Binary file content
        room_id: Chat room identifier
        filename: Original filename
        subdirectory: Optional subdirectory within room folder
    '''
    if not allowed_file(filename):
        raise ValueError("Invalid file type")

    # Sanitize the filename component
    safe_filename = secure_filename(filename)

    # Build path components
    base_path = os.path.join(UPLOAD_DIR, 'rooms', str(room_id))

    if subdirectory:
        # Allow nested organization within room
        target_dir = os.path.join(base_path, subdirectory)
    else:
        target_dir = base_path

    os.makedirs(target_dir, exist_ok=True)

    full_path = os.path.join(target_dir, safe_filename)

    with open(full_path, 'wb') as f:
        f.write(file_data)

    return full_path

def get_attachment_url(room_id, filename):
    '''Get URL for downloading an attachment'''
    return f"/api/rooms/{room_id}/attachments/{filename}"

def delete_attachment(room_id, filename):
    '''Delete a room attachment'''
    # Basic validation
    if '..' in filename or filename.startswith('/'):
        raise ValueError("Invalid filename")

    file_path = os.path.join(UPLOAD_DIR, 'rooms', str(room_id), filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
