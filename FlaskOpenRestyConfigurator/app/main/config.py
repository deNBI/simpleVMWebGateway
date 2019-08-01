import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    RESTPLUS_MASK_SWAGGER = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    RESTPLUS_MASK_SWAGGER = False

class ProductionConfig(Config):
    DEBUG = False
    RESTPLUS_MASK_SWAGGER = False

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY