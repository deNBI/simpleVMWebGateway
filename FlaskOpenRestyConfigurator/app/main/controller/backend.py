from flask_restplus import Resource
from ..util.auth import auth_required


from ..util.dto import BackendDto

api = BackendDto.api
_backend = BackendDto.backend

_createBackend = BackendDto.createBackend



@api.route('/')
class BackendsList(Resource):
    @api.doc("List of all registred backends", security="apikey")
    @api.marshal_list_with(_backend, envelope='data')
    @auth_required
    def get(self):
        pass


    @api.doc("Register a new backend", security="apikey")
    @api.expect(_createBackend, validate=True)
    @api.response(400, 'Validation error')
    @api.marshal_with(_backend, code=201, description="Backend created")
    def post(self):
        return "was"


