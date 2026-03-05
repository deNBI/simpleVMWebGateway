from app.main.model.serializers import BackendOut
import factory
from faker import Faker
import string
import random
fake = Faker()
def random_owner():
    allowed = string.ascii_letters + string.digits + "@"
    # mind. 30 chars
    return "".join(random.choices(allowed, k=30))

class BackendOutFactory(factory.DictFactory):
    id = factory.Sequence(lambda n: n + 1)
    
    owner = factory.LazyFunction(random_owner)
    template = "testtemplate"
    template_version = "v01"
    location_url = factory.Faker("url")
    config_path = factory.LazyAttribute(
        lambda o: f"{o.template}%{o.template_version}%0.conf"
    )

    class Meta:
        model = dict

def build_backend_out(**kwargs) -> BackendOut:
    """
    Helper that returns a validated BackendOut model.
    """
    return BackendOut.model_validate(
        BackendOutFactory.build(**kwargs)
    )