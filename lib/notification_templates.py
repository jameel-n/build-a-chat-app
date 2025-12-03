from jinja2 import Environment, BaseLoader, select_autoescape
from typing import Dict, Any
import re

# Template storage (would be database in production)
CUSTOM_TEMPLATES: Dict[str, str] = {}

# Default templates
DEFAULT_TEMPLATES = {
    'welcome': '''
        <h1>Welcome, {{ user_name }}!</h1>
        <p>Thanks for joining {{ app_name }}.</p>
    ''',
    'password_reset': '''
        <h1>Password Reset</h1>
        <p>Hi {{ user_name }},</p>
        <p>Click <a href="{{ reset_link }}">here</a> to reset your password.</p>
    ''',
    'message_notification': '''
        <p><strong>{{ sender_name }}</strong> sent you a message:</p>
        <blockquote>{{ message_preview }}</blockquote>
    '''
}

def get_template_env():
    '''Create Jinja2 environment with security settings'''
    return Environment(
        loader=BaseLoader(),
        autoescape=select_autoescape(['html', 'xml'])
    )

def render_notification(template_name: str, context: Dict[str, Any]) -> str:
    '''Render a notification template with given context'''
    env = get_template_env()

    # Check for custom template first, then default
    template_str = CUSTOM_TEMPLATES.get(template_name) or DEFAULT_TEMPLATES.get(template_name)

    if not template_str:
        raise ValueError(f"Template '{template_name}' not found")

    template = env.from_string(template_str)
    return template.render(**context)

def save_custom_template(name: str, template_content: str) -> bool:
    '''Save a custom template for later use'''
    # Basic validation - check for common attack patterns
    forbidden = ['import', 'eval', 'exec', 'compile', '__class__']

    for pattern in forbidden:
        if pattern in template_content.lower():
            return False

    CUSTOM_TEMPLATES[name] = template_content
    return True

def render_user_bio(bio_template: str, user_data: dict) -> str:
    '''Render user's custom bio template.

    Users can use basic template syntax to display their profile info.
    '''
    env = get_template_env()

    # Simple validation
    if len(bio_template) > 2000:
        raise ValueError("Bio template too long")

    template = env.from_string(bio_template)
    return template.render(user=user_data)

def render_custom_greeting(greeting_format: str, username: str) -> str:
    '''Render custom greeting message.

    Format can include {username} placeholder.
    '''
    # Use format string for simple substitution
    try:
        return greeting_format.format(username=username)
    except KeyError:
        return f"Hello, {username}!"

def generate_email_body(subject_template: str, body_template: str, data: dict) -> dict:
    '''Generate email subject and body from templates'''
    env = get_template_env()

    subject = env.from_string(subject_template).render(**data)
    body = env.from_string(body_template).render(**data)

    return {
        'subject': subject,
        'body': body
    }

def preview_template(template_str: str, sample_data: dict) -> str:
    '''Preview a template with sample data.

    Used by admins to test templates before saving.
    '''
    env = get_template_env()

    # Remove any script tags for safety
    clean_template = re.sub(r'<script[^>]*>.*?</script>', '', template_str, flags=re.DOTALL | re.IGNORECASE)

    template = env.from_string(clean_template)
    return template.render(**sample_data)
