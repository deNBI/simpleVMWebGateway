from flask import request
from flask_restplus import Resource

from ..util.dto import BackendDto

api = BackendDto.api
_backend = BackendDto.backend

_createBackend = BackendDto.createBackend


@api.route('/')
class BackendsList(Resource):

    @api.doc("List of all registred backends", security="apikey")
    @api.marshal_list_with(_backend, envelope='data')
    def get(self):
        return "dsf"


    @api.doc("Register a new backend", security="apikey")
    @api.expect(_createBackend)
    @api.marshal_with(_createBackend, envelope='data')
    def post(self):
        return "was"


