from flask_restplus import Api
from flask import Blueprint

from .main.controller.backend import api as backend_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='Flask OpenResty Configurator (FORC)',
          version='1.0',
          description="Endpoint for dynamic configuration of a running OpenResty server, acting as a ReverseProxy manager.")

api.add_namespace(backend_ns, path='')