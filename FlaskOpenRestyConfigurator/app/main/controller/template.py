from flask_restplus import Resource, abort
from ..util.auth import auth_required
from ..util.dto import TemplateDto
from ..service import template as template_service

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
        templates = template_service.get_templates()
        if not templates:
            return []
        return templates


@api.route('/<string:template_name>')
class TemplateByName(Resource):
    @api.doc("List of template versions", security="apikey", params={"template_name": "The template by name."})
    @api.marshal_list_with(_template)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'No Templates found')
    @auth_required
    def get(self, template_name):
        """Returns a list of all versions of the specified template."""
        if not template_name \
                or template_name is None \
                or not isinstance(template_name, str) \
                or len(template_name) == 0:
            abort(400)
        templates = template_service.get_templates(template_name)
        if not templates or len(templates) == 0:
            abort(404)
        return templates

@api.route('/<string:template_name>/<string:template_version>')
class TemplateByNameandVersion(Resource):
    @api.doc("Gets or checks a template", security="apikey",
             params={"template_name": "The template by name.",
                     "template_version": "The version of the wanted template"})
    @api.marshal_with(_template)
    @api.response(400, 'Invalid request')
    @api.response(401, 'Authorization error')
    @api.response(404, 'No Template with this version found found')
    @auth_required
    def get(self, template_name, template_version):
        """Gets or checks the existence of a specific template"""
        if not template_name \
                or template_name is None \
                or not isinstance(template_name, str) \
                or len(template_name) == 0:
            abort(400)
        if not template_version \
                or template_version is None \
                or not isinstance(template_version, str) \
                or len(template_version) == 0:
            abort(400)
        templates = template_service.get_templates(template_name, template_version)
        if not templates or len(templates) == 0 or len(templates) > 1:
            abort(404)
        return templates[0]
