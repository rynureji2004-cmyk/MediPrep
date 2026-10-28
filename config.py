import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configurations loading variables from environment."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
    # MySQL Database Settings
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'hospital_readiness_db')
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
    DB_POOL_NAME = os.environ.get('DB_POOL_NAME', 'hospital_pool')

    # Uploads Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB maximum file size limit

class DevelopmentConfig(Config):
    """Development configurations."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configurations."""
    TESTING = True
    DB_NAME = os.environ.get('DB_TEST_NAME', 'hospital_readiness_test_db')
    DEBUG = True

class ProductionConfig(Config):
    """Production configurations."""
    # Production values must be set via system env
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')

# Map environment configurations
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
