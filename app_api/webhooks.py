import requests
import json
import hmac
import hashlib
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify

webhooks_bp = Blueprint('webhooks', __name__)

BLOCKED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
WEBHOOK_TIMEOUT = 10
WEBHOOK_SECRET = 'webhook_signing_key_placeholder'

def validate_webhook_url(url):
    '''Validate that webhook URL is safe to call'''
    try:
        parsed = urlparse(url)

        # Must be http or https
        if parsed.scheme not in ('http', 'https'):
            return False, "Invalid scheme"

        # Block obvious localhost
        if parsed.hostname in BLOCKED_HOSTS:
            return False, "Localhost not allowed"

        # Block private IP notation
        if parsed.hostname and parsed.hostname.startswith('10.'):
            return False, "Private IP not allowed"

        return True, None
    except Exception as e:
        return False, str(e)

def sign_payload(payload: dict) -> str:
    '''Sign webhook payload for verification'''
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

@webhooks_bp.route('/api/webhooks/register', methods=['POST'])
def register_webhook():
    '''Register a new webhook endpoint'''
    data = request.get_json()

    url = data.get('url')
    events = data.get('events', ['message'])

    if not url:
        return jsonify({'error': 'URL required'}), 400

    valid, error = validate_webhook_url(url)
    if not valid:
        return jsonify({'error': error}), 400

    # Store webhook config (stub)
    webhook_id = hashlib.md5(url.encode()).hexdigest()[:8]

    return jsonify({
        'webhook_id': webhook_id,
        'url': url,
        'events': events
    })

@webhooks_bp.route('/api/webhooks/test', methods=['POST'])
def test_webhook():
    '''Test a webhook by sending a sample payload'''
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    valid, error = validate_webhook_url(url)
    if not valid:
        return jsonify({'error': error}), 400

    test_payload = {
        'event': 'test',
        'timestamp': 1234567890,
        'data': {'message': 'Webhook test successful'}
    }

    signature = sign_payload(test_payload)

    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={'X-Webhook-Signature': signature},
            timeout=WEBHOOK_TIMEOUT
        )
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response_preview': response.text[:200]
        })
    except requests.RequestException as e:
        return jsonify({'success': False, 'error': str(e)})


def fetch_user_avatar_url(avatar_url):
    '''Fetch and validate user avatar from external URL.

    Used during user import from external systems.
    '''
    # Basic URL validation
    parsed = urlparse(avatar_url)
    if parsed.scheme not in ('http', 'https'):
        return None

    try:
        response = requests.get(avatar_url, timeout=5, stream=True)
        content_type = response.headers.get('content-type', '')

        if not content_type.startswith('image/'):
            return None

        # Read up to 5MB
        return response.content[:5 * 1024 * 1024]
    except Exception:
        return None


@webhooks_bp.route('/api/preview/link', methods=['POST'])
def preview_link():
    '''Generate link preview by fetching URL metadata'''
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL required'}), 400

    # Only allow http/https
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return jsonify({'error': 'Invalid URL scheme'}), 400

    try:
        response = requests.get(
            url,
            timeout=5,
            headers={'User-Agent': 'ChatApp-LinkPreview/1.0'},
            allow_redirects=True
        )

        # Extract basic metadata (simplified)
        content = response.text[:50000]
        title = extract_title(content)
        description = extract_meta_description(content)

        return jsonify({
            'url': url,
            'title': title,
            'description': description,
            'final_url': response.url
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch URL'}), 400


def extract_title(html):
    '''Extract title from HTML'''
    import re
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_meta_description(html):
    '''Extract meta description from HTML'''
    import re
    match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else None
