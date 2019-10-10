from flask_restplus import Resource
from ..util.auth import auth_required
from ..util.dto import BackendDto
from ..service import backend as backend_service


from werkzeug.exceptions import BadRequest, NotFound

api = BackendDto.api
_backend = BackendDto.backend
_createBackend = BackendDto.createBackend


@api.route('/')
class BackendsList(Resource):
    @api.doc("List of all registred backends", security="apikey")
    @api.marshal_list_with(_backend, skip_none=True)
    @api.response(400, 'Invalid Request')
    @api.response(401, 'Authorization error')
    @auth_required
    def get(self):
        """List all registered users"""
        backends = backend_service.getBackends()
        if not backends:
            return []
        return backends


    @api.doc("Register a new oidc protected backend", security="apikey")
    @api.expect(_createBackend, validate=True)
    @api.response(400, 'Validation error')
    @api.response(401, 'Authorization error')
    @api.marshal_with(_backend, code=200, description="Backend created")
    @api.expect(_createBackend)
    @auth_required
    def post(self):
        """Register a new oidc protected backend"""
        if api.payload:
            modifiedPayload = backend_service.createBackend(api.payload)
            return modifiedPayload
        else:
            raise BadRequest


@api.route('/<int:backendID>')
class Backend(Resource):
    @api.doc("Specified backend by id", security="apikey", params={"backendID" : "ID of backend to return."})
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Backend not found')
    @api.marshal_with(_backend, code=200, description="Backend found.")
    @auth_required
    def get(self, backendID):
        """Returns a specific backend by id"""
        backends = backend_service.getBackends()
        if not backends:
            raise BadRequest
        for backend in backends:
            if int(backend["id"]) == int(backendID):
                return backend
        raise NotFound

    @api.doc("Specified backend by id", security="apikey", params={"backendID" : "ID of backend to delete."})
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'Backend not found')
    @api.response(200, 'Backend deleted.')
    @auth_required
    def delete(self, backendID):
        """Deletes a specific backend by id"""
        backend_service.deleteBackend(backendID)
        return {"message" : "Backend deleted: " + str(backendID)}




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
        backends = backend_service.getBackends()
        if not backends:
            raise BadRequest
        backendsByOwner = []
        for backend in backends:
            if backend["owner"] == owner:
                backendsByOwner.append(backend)
        if backendsByOwner:
            return backendsByOwner
        else:
            raise NotFound


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
        backends = backend_service.getBackends()
        if not backends:
            raise BadRequest
        backendsByTemplate = []
        for backend in backends:
            if backend["template"] == template:
                backendsByTemplate.append(backend)
        if backendsByTemplate:
            return backendsByTemplate
        else:
            raise NotFound("No backends with such template found.")



