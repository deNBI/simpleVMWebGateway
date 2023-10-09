from flask_restplus import Namespace, fields


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}


# General DTO for a backend json object
class BackendDto:
    api = Namespace('backends', description="All backend related resources. Backends are generated nginx location snippets, generated from templates.", authorizations=authorizations)

    backend = api.model('Backend', {
        'id': fields.Integer(required=True, description="Unique ID of backend", example="78345"),
        'owner': fields.String(required=True, description="User who owns this backend."),
        'location_url': fields.String(required=True, description="Protected reverse-proxy path which leads to specific backend"),
        'template': fields.String(required=True, description="Used backend template", example="rstudio"),
        'template_version': fields.String(required=True, description="Template Version", example="v1")
    })

    createBackend = api.model('CreateBackend', {
        'owner': fields.String(required=True, description="User who owns this backend.", example="21894723853fhdzug92"),
        'user_key_url': fields.String(required=True, description="User set location url prefix", example="myFavoriteRstudio"),
        'upstream_url': fields.String(required=True, description="Inject the full url (with protocol) for the real location of the backend service in the template.", example="http://localhost:7001/"),
        'template': fields.String(required=True, description="Used backend template", example="rstudio"),
        'template_version': fields.String(required=True, description="Template Version", example="v1")
    })


class UserDto:
    api = Namespace('users', description="All user related endpoints. Users are people allowed to access a backend.", authorizations=authorizations)

    createUser = api.model('createUser', {
        'owner': fields.String(required=True, description="User who owns this backend. "),
        'user': fields.String(required=True, description="User who will be added to this backend.")
    })


# General DTO for a template json object
class TemplateDto:
    api = Namespace('templates', description="All template related endpoints. Templates are used to generate OpenResty location configurations.", authorizations=authorizations)

    template = api.model('Template', {
        'name': fields.String(required=True, description="Name of the template.", example="rstudio"),
        'version': fields.String(required=True, description="Version of this template.", example="v13")
    })


class UtilsDto:
    api = Namespace('utils', description="Misc endpoints.", authorizations=authorizations)

    version = api.model('Version', {
        'version': fields.String(required=True, description="Current running version of this service framework", example="v1.0.0")
    })
