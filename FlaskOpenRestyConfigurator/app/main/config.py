import os

FORC_VERSION = '0.1a'

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('FORC_SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    RESTPLUS_MASK_SWAGGER = False
    SWAGGER_BASEPATH = '/config'

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
api_key = os.getenv("FORC_API_KEY")

#todo read from environment variable

backend_path = os.getenv("FORC_BACKEND_PATH")
user_path = "{0}/users".format(backend_path)
templates_path = os.getenv("FORC_TEMPLATE_PATH")
#backend_path = '/home/ubuntu/forc_config/backends/'
#templates_path = '/home/ubuntu/forc_config/templates/'

