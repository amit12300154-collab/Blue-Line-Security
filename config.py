import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
# Load .env file
load_dotenv(basedir / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'blue-line-insecure-dev-key-change-me')
    
    # SQLite default path inside instance/
    db_path = basedir / 'instance' / 'blue_line.db'
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and not raw_db_url.startswith('sqlite:///instance/'):
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.resolve().as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie hardening (SameSite=Lax blocks cross-site form POSTs)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    
    # Demo Mode setting
    DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() in ('true', '1', 't', 'yes')
    
    # Emergency sensors & timer defaults
    IMPACT_THRESHOLD = float(os.environ.get('IMPACT_THRESHOLD', 25.0))
    EMERGENCY_COUNTDOWN = int(os.environ.get('EMERGENCY_COUNTDOWN', 10))
    
    # SMTP / Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't', 'yes')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'alerts@blueline.local')
    
    # Seed Accounts
    ADMIN_DEFAULT_EMAIL = os.environ.get('ADMIN_DEFAULT_EMAIL', 'admin@blueline.local')
    ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'Admin@12345')
    DEMO_USER_EMAIL = os.environ.get('DEMO_USER_EMAIL', 'demo@example.com')
    DEMO_USER_PASSWORD = os.environ.get('DEMO_USER_PASSWORD', 'Demo@12345')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


from sqlalchemy.pool import StaticPool


class TestingConfig(Config):
    """Testing configuration with in-memory database."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False},
        'poolclass': StaticPool
    }
    WTF_CSRF_ENABLED = False
    DEMO_MODE = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # requires HTTPS
    REMEMBER_COOKIE_SECURE = True


config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
