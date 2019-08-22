from flask_restplus import Resource
from ..util.auth import auth_required
from ..util.dto import BackendDto


api = BackendDto.api
_backend = BackendDto.backend
_createBackend = BackendDto.createBackend


@api.route('/')
class BackendsList(Resource):
    @api.doc("List of all registred backends", security="apikey")
    @api.marshal_list_with(_backend)
    @api.response(401, 'Authorization error')
    @auth_required
    def get(self):
        """List all registered users"""
        return "blabla"


    @api.doc("Register a new oidc protected backend", security="apikey")
    @api.expect(_createBackend, validate=True)
    @api.response(400, 'Validation error')
    @api.response(401, 'Authorization error')
    @api.marshal_with(_backend, code=201, description="Backend created")
    @auth_required
    def post(self):
        """Register a new oidc protected backend"""
        pass

@api.route('/<int:backendID>')
class Backend(Resource):
    @api.doc("Specified backend by id", security="apikey", params={"backendID" : "ID of backend to return."})
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Backend not found')
    @api.marshal_with(_backend, code=201, description="Backend found.")
    @auth_required
    def get(self):
        """Returns a specific backend by id"""
        pass

    @api.doc("Specified backend by id", security="apikey", params={"backendID" : "ID of backend to delete."})
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Backend not found')
    @api.marshal_with(_backend, code=201, description="Backend deleted.")
    @auth_required
    def delete(self):
        """Deletes a specific backend by id"""
        pass




@api.route('/byOwner/<string:owner>')
class BackendsByOwner(Resource):
    @api.doc("Returns a list of all owner specified backends.", security="apikey", params={'owner': "The ELIXIR Owner without @elixir.org suffix"})
    @api.marshal_list_with(_backend)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Owner not found.')
    @auth_required
    def get(self, owner):
        """Returns a list of all owner specified backends."""
        pass


@api.route('/byTemplate/<string:template>')
class BackendsByTemplate(Resource):
    @api.doc("Returns a list of all backends based on a specific template.", security="apikey", params={'template': "The targeted template by name."})
    @api.marshal_list_with(_backend)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Template not found.')
    @auth_required
    def get(self, template):
        """Returns a list of all backends based on a specific template."""
        pass



