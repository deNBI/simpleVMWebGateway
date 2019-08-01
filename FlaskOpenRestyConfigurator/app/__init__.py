from flask_restplus import Api
from flask import Blueprint

from .main.controller.backend import api as backend_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='Test',
          version='1.0',
          description="test bla")

api.add_namespace(backend_ns, path='')