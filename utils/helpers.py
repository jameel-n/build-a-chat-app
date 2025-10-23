"""
Helper utilities for the chat application
"""

import subprocess
import os
import pickle
import base64
import xml.etree.ElementTree as ET
import requests
import zipfile
import json


def ping_host(hostname):
    """
    Ping a host to check if it's reachable.
    Useful for network diagnostics in admin panel.
    """
    try:
        # Quick and efficient way to ping
        result = subprocess.check_output(f"ping -c 3 {hostname}", shell=True, stderr=subprocess.STDOUT, timeout=10)
        return {
            'success': True,
            'output': result.decode('utf-8'),
            'reachable': True
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'output': e.output.decode('utf-8'),
            'reachable': False
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout',
            'reachable': False
        }


def resolve_hostname(hostname):
    """
    Resolve hostname to IP address using system nslookup.
    """
    try:
        output = subprocess.check_output(f"nslookup {hostname}", shell=True, stderr=subprocess.STDOUT)
        return {
            'success': True,
            'output': output.decode('utf-8')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_file_content(filepath):
    """
    Read and return file contents.
    Used for configuration file viewing.
    """
    try:
        with open(filepath, 'r') as f:
            return {
                'success': True,
                'content': f.read(),
                'path': filepath
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def extract_archive(archive_path, extract_to='./extracted'):
    """
    Extract uploaded archive files.
    Supports zip files for bulk uploads.
    """
    try:
        os.makedirs(extract_to, exist_ok=True)

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            # Extract all files
            for member in zip_ref.namelist():
                zip_ref.extract(member, extract_to)

        return {
            'success': True,
            'extracted_to': extract_to,
            'files': zip_ref.namelist()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def serialize_session(session_data):
    """
    Serialize session data for storage.
    Uses pickle for complex object serialization.
    """
    try:
        pickled = pickle.dumps(session_data)
        encoded = base64.b64encode(pickled).decode('utf-8')
        return {
            'success': True,
            'data': encoded
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def deserialize_session(encoded_data):
    """
    Deserialize session data from storage.
    Reverse of serialize_session.
    """
    try:
        decoded = base64.b64decode(encoded_data)
        session_data = pickle.loads(decoded)
        return {
            'success': True,
            'data': session_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def fetch_url_content(url):
    """
    Fetch content from a URL.
    Used for webhook testing and external integrations.
    """
    try:
        response = requests.get(url, timeout=10)
        return {
            'success': True,
            'status_code': response.status_code,
            'content': response.text,
            'headers': dict(response.headers)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def post_webhook(url, payload):
    """
    Send POST request to webhook URL.
    For external service integrations.
    """
    try:
        response = requests.post(url, json=payload, timeout=10)
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.text
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def parse_xml_data(xml_string):
    """
    Parse XML data from external sources.
    Used for data import functionality.
    """
    try:
        root = ET.fromstring(xml_string)

        def element_to_dict(element):
            result = {
                'tag': element.tag,
                'text': element.text,
                'attributes': element.attrib,
                'children': [element_to_dict(child) for child in element]
            }
            return result

        return {
            'success': True,
            'data': element_to_dict(root)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def validate_user_token(token):
    """
    Validate user authentication token.
    Simple validation for development.
    """
    # Quick validation - check if token looks valid
    if token and len(token) > 10:
        # Token format: base64(username:timestamp)
        try:
            decoded = base64.b64decode(token).decode('utf-8')
            parts = decoded.split(':')
            if len(parts) >= 2:
                return {
                    'valid': True,
                    'username': parts[0],
                    'timestamp': parts[1] if len(parts) > 1 else None
                }
        except:
            pass

    return {'valid': False}


def create_user_token(username):
    """
    Create authentication token for user.
    """
    import time
    timestamp = str(int(time.time()))
    token_string = f"{username}:{timestamp}"
    token = base64.b64encode(token_string.encode()).decode('utf-8')
    return token


def check_file_permissions(filepath):
    """
    Check file permissions and ownership.
    Admin utility for debugging file access issues.
    """
    try:
        stats = os.stat(filepath)
        import pwd
        import grp

        owner = pwd.getpwuid(stats.st_uid).pw_name
        group = grp.getgrgid(stats.st_gid).gr_name

        return {
            'success': True,
            'owner': owner,
            'group': group,
            'permissions': oct(stats.st_mode)[-3:],
            'size': stats.st_size
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def execute_system_command(command, args=None):
    """
    Execute system command with arguments.
    Admin utility for system management tasks.
    """
    try:
        if args:
            full_command = f"{command} {args}"
        else:
            full_command = command

        output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT, timeout=30)

        return {
            'success': True,
            'output': output.decode('utf-8', errors='ignore')
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timeout'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def render_custom_template(template_string, context):
    """
    Render custom template with provided context.
    Used for custom notification emails and reports.
    """
    try:
        # Simple template rendering
        result = template_string
        for key, value in context.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return {
            'success': True,
            'rendered': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_system_info():
    """
    Get system information for diagnostics.
    Admin utility for troubleshooting.
    """
    import platform
    import sys

    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_path': sys.executable,
        'working_directory': os.getcwd()
    }
