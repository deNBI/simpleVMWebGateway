from flask_restplus import Resource
from ..util.auth import auth_required
from ..util.dto import UserDto
from ..service import user as user_service


from werkzeug.exceptions import BadRequest, InternalServerError

api = UserDto.api
_createUser = UserDto.createUser


@api.route('/<int:backend_id>')
class User(Resource):
    @api.doc("List of all users for a backend", security="apikey", params={"backend_id": "ID of backend to check."})
    @api.response(400, 'Invalid Request')
    @api.response(401, 'Authorization error')
    @auth_required
    def get(self, backend_id):
        """List all registered users"""
        users = user_service.get_users(str(backend_id))
        if not users:
            return []
        return users

    @api.doc("Add a new user to a backend", security="apikey", params={"backend_id": "ID of backend."})
    @api.expect(_createUser, validate=True)
    @api.response(400, 'Validation error')
    @api.response(401, 'Authorization error')
    @api.response(500, 'Internal server error')
    @api.marshal_with(_createUser, code=200, description="User added")
    @auth_required
    def post(self, backend_id):
        """Add a new user to a backend"""
        if api.payload:
            res = user_service.add_user(str(backend_id), api.payload["user"])
            if res != 0:
                raise InternalServerError
            else:
                return api.payload
        else:
            raise BadRequest

    @api.doc("Delete user from a backend", security="apikey", params={"backend_id": "ID of backend."})
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'User not found')
    @api.response(200, 'User deleted.')
    @auth_required
    def delete(self, backend_id):
        """Deletes a specific backend by id"""
        user_service.delete_user(backend_id, api.payload["user"])
        return {"message": "User {0} deleted from {1}.".format(api.payload["user"], backend_id)}
