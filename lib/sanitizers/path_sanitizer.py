import os
import re

def clean(filename):
    '''Sanitize file paths to prevent directory traversal attacks.

    Removes:
    - Parent directory references (..)
    - Absolute paths (/)
    - Null bytes
    '''
    # Remove null bytes
    filename = filename.replace('\0', '')

    # Remove path traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')

    # Only allow alphanumeric, dash, underscore, dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

    return filename
