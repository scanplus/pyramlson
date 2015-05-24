import logging
import ramlfications
from zope.interface import Interface

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

log = logging.getLogger(__name__)


class IRamlApiDefinition(Interface):
        pass


class RamlApiDefinition(object):

    __traits_cache = {}

    def __init__(self, apidef_path):
        self.raml = ramlfications.parse(apidef_path)
        self.base_uri = self.raml.base_uri
        self.base_path = urlparse(self.base_uri).path

    def get_trait(self, name):
        if not self.raml.traits:
            return None
        trait = None
        if name not in self.__traits_cache:
            for trait in self.raml.traits:
                if trait.name == name:
                    self.__traits_cache[name] = trait
        return self.__traits_cache.get(name)

    def get_resource_traits(self, resource):
        if not resource.traits:
            return dict()
        ret = dict()
        for trait in resource.traits:
            ret[trait.name] = self.get_trait(trait.name)
        return ret

    def get_resources(self, prefix=None):
        if not prefix:
            return self.raml.resources
        return (res for res in self.raml.resources if res.path.startswith(prefix))

    def get_schema_def(self, name):
        for schemas in self.raml.schemas:
            if name in schemas:
                return schemas[name]

    def get_schema(self, resource, mime_type='application/json'):
        # FIXME Support xml
        if not resource.body:
            return None
        body = None
        for b in resource.body:
            if b.mime_type != mime_type:
                continue
            body = b
            break
        if not body or not body.schema:
            return None
        schema = body.schema
        # FIXME there should be a better way to detect an inline schema
        if '$schema' not in schema:
            schema = self.get_schema_def(schema)
        return schema
