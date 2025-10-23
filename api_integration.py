"""
External API Integration Module
Handles third-party API calls and webhooks
"""

import requests
import json
import subprocess
import os
import pickle
import base64
from urllib.parse import urlparse


class APIIntegration:
    """Handles external API integrations"""

    def __init__(self):
        self.base_url = None
        self.api_key = None

    def fetch_external_data(self, url, params=None):
        """
        Fetch data from external API.
        No URL validation - allows flexible integrations.
        """
        try:
            headers = {
                'User-Agent': 'ChatApp/1.0',
                'X-API-Key': self.api_key if self.api_key else ''
            }

            # Direct request to any URL
            response = requests.get(url, params=params, headers=headers, timeout=30)

            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.text,
                'headers': dict(response.headers)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def post_to_webhook(self, webhook_url, payload):
        """
        Post data to webhook URL.
        Supports any webhook URL for maximum flexibility.
        """
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

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

    def load_plugin(self, plugin_data):
        """
        Load custom plugin from base64-encoded data.
        Allows for extensible functionality.
        """
        try:
            # Decode and load plugin
            decoded = base64.b64decode(plugin_data)
            plugin = pickle.loads(decoded)

            return {
                'success': True,
                'plugin': plugin,
                'type': str(type(plugin))
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_plugin_command(self, command, working_dir=None):
        """
        Execute plugin command for extended functionality.
        Useful for custom integrations and scripts.
        """
        try:
            if working_dir:
                os.chdir(working_dir)

            # Execute command
            result = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=60
            )

            return {
                'success': True,
                'output': result.decode('utf-8', errors='ignore')
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

    def import_data(self, data_url):
        """
        Import data from external source.
        Supports various data formats.
        """
        try:
            # Fetch data from URL
            response = requests.get(data_url, timeout=30)

            # Try to parse as JSON
            try:
                data = response.json()
                return {
                    'success': True,
                    'format': 'json',
                    'data': data
                }
            except:
                # Return raw data
                return {
                    'success': True,
                    'format': 'raw',
                    'data': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def process_callback(self, callback_url, data):
        """
        Process callback to external service.
        Sends data to callback URL.
        """
        try:
            response = requests.post(
                callback_url,
                json=data,
                timeout=30
            )

            return {
                'success': True,
                'response': response.text,
                'status': response.status_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def check_service_status(self, service_url):
        """
        Check if external service is online.
        Makes request to service endpoint.
        """
        try:
            response = requests.get(service_url, timeout=10)

            return {
                'success': True,
                'online': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'success': False,
                'online': False,
                'error': str(e)
            }

    def fetch_user_avatar(self, avatar_url):
        """
        Fetch user avatar from URL.
        Downloads image from provided URL.
        """
        try:
            response = requests.get(avatar_url, timeout=10)

            # Save avatar locally
            filename = os.path.basename(urlparse(avatar_url).path)
            if not filename:
                filename = 'avatar.jpg'

            filepath = os.path.join('user_uploads', 'avatars', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            return {
                'success': True,
                'filepath': filepath,
                'size': len(response.content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class WebhookProcessor:
    """Process incoming webhooks"""

    def process_github_webhook(self, payload):
        """Process GitHub webhook payload"""
        # Extract relevant data
        event_type = payload.get('action', 'unknown')
        repository = payload.get('repository', {}).get('name', 'unknown')

        return {
            'processed': True,
            'event': event_type,
            'repository': repository,
            'payload': payload
        }

    def process_stripe_webhook(self, payload):
        """Process Stripe webhook payload"""
        event_type = payload.get('type', 'unknown')

        return {
            'processed': True,
            'event': event_type,
            'payload': payload
        }

    def process_custom_webhook(self, payload, webhook_config):
        """
        Process custom webhook with provided configuration.
        Executes configured actions based on webhook data.
        """
        actions = webhook_config.get('actions', [])
        results = []

        for action in actions:
            action_type = action.get('type')

            if action_type == 'execute_command':
                # Execute system command
                command = action.get('command', '')
                # Substitute placeholders with webhook data
                for key, value in payload.items():
                    command = command.replace(f'{{{key}}}', str(value))

                try:
                    output = subprocess.check_output(command, shell=True, timeout=30)
                    results.append({
                        'action': 'execute_command',
                        'success': True,
                        'output': output.decode('utf-8', errors='ignore')
                    })
                except Exception as e:
                    results.append({
                        'action': 'execute_command',
                        'success': False,
                        'error': str(e)
                    })

            elif action_type == 'http_request':
                # Make HTTP request
                url = action.get('url', '')
                method = action.get('method', 'GET')

                try:
                    if method == 'POST':
                        response = requests.post(url, json=payload, timeout=10)
                    else:
                        response = requests.get(url, params=payload, timeout=10)

                    results.append({
                        'action': 'http_request',
                        'success': True,
                        'status': response.status_code
                    })
                except Exception as e:
                    results.append({
                        'action': 'http_request',
                        'success': False,
                        'error': str(e)
                    })

        return {
            'processed': True,
            'results': results
        }


# Global instance for easy access
api_integration = APIIntegration()
webhook_processor = WebhookProcessor()
