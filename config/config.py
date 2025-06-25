import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(base_dir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'defaultkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv('REDIS_URL')
    CORS_HEADERS = 'Content-Type'

    # -------------------------------
    # OAuth / Social login settings
    # -------------------------------
    # Domyślnie zakazujemy insecure transport (wykorzystuj HTTPS)
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '0')
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID     = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    # (Tu możesz później dodać np. GitHub, Facebook itd.)
    # GITHUB_OAUTH_CLIENT_ID     = os.getenv('GITHUB_OAUTH_CLIENT_ID')
    # GITHUB_OAUTH_CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    # W development pozwalamy na HTTP (niezalecane w prod!)
    OAUTHLIB_INSECURE_TRANSPORT = '1'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    # W prod wykorzystuj wyłącznie HTTPS, więc nie zmieniamy OAUTHLIB_INSECURE_TRANSPORT

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # W testach też możemy zezwolić na insecure transport, by testować OAuth bez HTTPS
    OAUTHLIB_INSECURE_TRANSPORT = '1'

config_dict = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig
}