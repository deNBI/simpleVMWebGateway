from flask_restplus import Resource
from ..util.dto import UtilsDto


api = UtilsDto.api
_version = UtilsDto.version

@api.route('/')
class Version(Resource):
    @api.doc("List of all registred backends")
    @api.marshal_with(_version)
    @api.response(400, 'Invalid Request')
    def get(self):
        """Returns the current version of this service framework."""
        return "blabla"