from flask_restplus import Api
from flask import Blueprint

from .main.controller.backend import api as backend_ns
from .main.controller.template import api as template_ns
from .main.controller.utils import api as utils_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='Flask OpenResty Configurator (FORC)',
          version='0.1a',
          description="Endpoint for dynamic configuration of a running OpenResty server, acting as a ReverseProxy manager.")

api.add_namespace(backend_ns, path='')
api.add_namespace(template_ns, path='')
api.add_namespace(utils_ns, path='')