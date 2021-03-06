import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api
from flask import Blueprint

from .main.controller.backend import api as backend_ns
from .main.controller.template import api as template_ns
from .main.controller.utils import api as utils_ns
from .main.controller.user import api as user_ns

from .main.config import FORC_VERSION

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='Flask OpenResty Configurator (FORC)',
          version=FORC_VERSION,
          description="Endpoint for dynamic configuration of a running OpenResty server, acting as a ReverseProxy manager.")

api.add_namespace(backend_ns, path='')
api.add_namespace(template_ns, path='')
api.add_namespace(utils_ns, path='')
api.add_namespace(user_ns, path='')
