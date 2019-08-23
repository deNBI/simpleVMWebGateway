from flask_restplus import Resource
from ..util.auth import auth_required
from ..util.dto import TemplateDto
from ..service import template as template_service
from werkzeug.exceptions import BadRequest

api = TemplateDto.api
_template = TemplateDto.template


@api.route('/')
class TemplatesList(Resource):
    @api.doc("List of all found templates", security="apikey")
    @api.marshal_list_with(_template, skip_none=True)
    @api.response(401, 'Authorization error')
    @auth_required
    def get(self):
        """List all registered templates"""
        templates = template_service.getTemplates()
        if not templates:
            return []
        return templates


@api.route('/<string:templateName>')
class TemplateByName(Resource):
    @api.doc("List of template versions", security="apikey", params={"templateName" : "The template by name."})
    @api.marshal_list_with(_template)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'No Templates found')
    @auth_required
    def get(self, templateName):
        """Returns a list of all versions of the specified template."""
        pass

@api.route('/<string:templateName>/<string:templateVersion>')
class TemplateByNameandVersion(Resource):
    @api.doc("Gets or checks a template", security="apikey", params={"templateName" : "The template by name.", "templateVersion" : "The version of the wanted template"})
    @api.marshal_with(_template)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'No Template with this version found found')
    @auth_required
    def get(self, templateName, templateVersion):
        """Gets or checks the existence of a specific template"""
        pass