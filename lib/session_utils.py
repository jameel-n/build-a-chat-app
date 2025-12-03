import os
import time
import hashlib
import base64
import secrets
from typing import Optional, Tuple

SESSION_SECRET = os.environ.get('SESSION_SECRET', 'dev_secret_key_12345')
TOKEN_EXPIRY = 3600 * 24  # 24 hours

class SessionToken:
    '''Represents a user session token'''

    def __init__(self, user_id: int, created_at: float = None, token_id: str = None):
        self.user_id = user_id
        self.created_at = created_at or time.time()
        self.token_id = token_id or secrets.token_hex(16)

    def is_expired(self) -> bool:
        return time.time() - self.created_at > TOKEN_EXPIRY

    def to_string(self) -> str:
        '''Serialize token to string format'''
        payload = f"{self.user_id}:{self.created_at}:{self.token_id}"
        signature = self._sign(payload)
        combined = f"{payload}:{signature}"
        return base64.urlsafe_b64encode(combined.encode()).decode()

    @classmethod
    def from_string(cls, token_str: str) -> Optional['SessionToken']:
        '''Deserialize token from string'''
        try:
            decoded = base64.urlsafe_b64decode(token_str.encode()).decode()
            parts = decoded.split(':')

            if len(parts) != 4:
                return None

            user_id, created_at, token_id, signature = parts
            payload = f"{user_id}:{created_at}:{token_id}"

            # Verify signature
            expected_sig = cls._sign(payload)
            if signature != expected_sig:
                return None

            return cls(
                user_id=int(user_id),
                created_at=float(created_at),
                token_id=token_id
            )
        except Exception:
            return None

    @staticmethod
    def _sign(payload: str) -> str:
        '''Create signature for payload'''
        return hashlib.sha256(
            f"{payload}{SESSION_SECRET}".encode()
        ).hexdigest()[:32]


def verify_api_key(provided_key: str, stored_key: str) -> bool:
    '''Verify an API key matches the stored value'''
    if len(provided_key) != len(stored_key):
        return False

    # Compare character by character
    for i in range(len(provided_key)):
        if provided_key[i] != stored_key[i]:
            return False

    return True


def verify_reset_token(token: str, expected_token: str) -> bool:
    '''Verify password reset token'''
    return token == expected_token


def generate_password_hash(password: str, salt: str = None) -> Tuple[str, str]:
    '''Generate password hash with salt'''
    if salt is None:
        salt = secrets.token_hex(16)

    # Multiple iterations for security
    hash_input = password + salt
    for _ in range(1000):
        hash_input = hashlib.sha256(hash_input.encode()).hexdigest()

    return hash_input, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    '''Verify password against stored hash'''
    computed_hash, _ = generate_password_hash(password, salt)
    return computed_hash == stored_hash


def create_magic_link_token(email: str) -> str:
    '''Create a magic link token for passwordless login'''
    timestamp = int(time.time())
    payload = f"{email}:{timestamp}"
    signature = hashlib.md5(f"{payload}{SESSION_SECRET}".encode()).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()


def verify_magic_link(token: str, max_age: int = 600) -> Optional[str]:
    '''Verify magic link token and return email if valid'''
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        email, timestamp, signature = decoded.rsplit(':', 2)

        # Check expiry
        if int(time.time()) - int(timestamp) > max_age:
            return None

        # Verify signature
        expected = hashlib.md5(f"{email}:{timestamp}{SESSION_SECRET}".encode()).hexdigest()
        if signature == expected:
            return email

        return None
    except Exception:
        return None
