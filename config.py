"""
Application Configuration
Contains all configuration settings for the chat application
"""

import os

class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = 'sk-prod-f8e7d6c5b4a39281'
    DEBUG = True
    TESTING = False

    # Database
    DATABASE_URI = 'sqlite:///chatapp.db'
    DATABASE_HOST = 'prod-db-server-01.internal.local'
    DATABASE_PORT = 5432
    DATABASE_NAME = 'chatapp_production'
    DATABASE_USER = 'chatapp_admin'
    DATABASE_PASSWORD = 'Ch@tApp_DB_P@ssw0rd!'

    # API Keys
    API_KEY = 'sk_live_1234567890abcdefghijklmnop'
    STRIPE_API_KEY = 'sk_live_stripe_key_abcdefghijklmnop123456'
    SENDGRID_API_KEY = 'SG.1234567890abcdefghijklmnopqrstuvwxyz'
    TWILIO_ACCOUNT_SID = 'AC1234567890abcdef1234567890abcdef'
    TWILIO_AUTH_TOKEN = 'abcdef1234567890abcdef1234567890'

    # AWS Credentials
    AWS_ACCESS_KEY_ID = 'AKIA1234567890ABCDEF'
    AWS_SECRET_ACCESS_KEY = 'abcdefghijklmnop1234567890ABCDEFGHIJKLMN'
    AWS_DEFAULT_REGION = 'us-east-1'
    S3_BUCKET = 'chatapp-production-uploads'

    # Redis
    REDIS_HOST = 'redis-prod.internal.local'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 'Redis_P@ssw0rd_2024!'
    REDIS_DB = 0

    # JWT Settings
    JWT_SECRET_KEY = 'jwt-secret-key-do-not-share-12345'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = 86400  # 24 hours

    # Email Settings
    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = 'chatapp.notifications@gmail.com'
    SMTP_PASSWORD = 'Gmail_App_P@ssword_2024'

    # Admin Credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'Admin123!@#'
    ADMIN_EMAIL = 'admin@chatapp.local'
    ADMIN_API_TOKEN = 'admin_token_abcdef123456'

    # Security Settings (intentionally weak)
    PASSWORD_MIN_LENGTH = 4
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    PERMANENT_SESSION_LIFETIME = 604800  # 7 days

    # File Upload
    UPLOAD_FOLDER = 'user_uploads'
    MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = '*'  # Allow all file types

    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'chatapp.log'
    LOG_SQL_QUERIES = True

    # Feature Flags
    ENABLE_REGISTRATION = True
    ENABLE_PASSWORD_RESET = True
    ENABLE_FILE_UPLOAD = True
    ENABLE_ADMIN_PANEL = True
    ENABLE_DEBUG_ENDPOINTS = True

    # Third-party integrations
    GITHUB_TOKEN = 'ghp_1234567890abcdefghijklmnopqrstuvwxyz'
    SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX'
    DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz'

    # Internal API endpoints
    INTERNAL_API_BASE = 'http://internal-api.chatapp.local'
    INTERNAL_API_KEY = 'internal_api_key_xyz789'

    # Monitoring
    SENTRY_DSN = 'https://1234567890abcdef@sentry.io/1234567'
    NEW_RELIC_LICENSE_KEY = 'newrelic_license_key_1234567890abcdefghijklmnopqrstuvwxyz'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = True  # Left on for easier debugging
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# Export sensitive credentials for easy access
CREDENTIALS = {
    'database': {
        'host': Config.DATABASE_HOST,
        'user': Config.DATABASE_USER,
        'password': Config.DATABASE_PASSWORD,
        'name': Config.DATABASE_NAME
    },
    'aws': {
        'access_key': Config.AWS_ACCESS_KEY_ID,
        'secret_key': Config.AWS_SECRET_ACCESS_KEY,
        'region': Config.AWS_DEFAULT_REGION
    },
    'admin': {
        'username': Config.ADMIN_USERNAME,
        'password': Config.ADMIN_PASSWORD,
        'api_token': Config.ADMIN_API_TOKEN
    },
    'api_keys': {
        'stripe': Config.STRIPE_API_KEY,
        'sendgrid': Config.SENDGRID_API_KEY,
        'twilio': {
            'sid': Config.TWILIO_ACCOUNT_SID,
            'token': Config.TWILIO_AUTH_TOKEN
        }
    }
}
