from flask import Flask
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix


from .config import config_by_name

def create_app(config_name):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config.from_object(config_by_name[config_name])

    return app