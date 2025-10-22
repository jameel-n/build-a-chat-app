import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
ALLOWED_ATTRIBUTES = {}

def clean(user_input):
    '''Sanitize HTML input to prevent XSS attacks.

    Used across the application to clean user-generated content.
    '''
    return bleach.clean(user_input, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def clean_strict(user_input):
    '''Strip all HTML tags'''
    return bleach.clean(user_input, tags=[], attributes={}, strip=True)
