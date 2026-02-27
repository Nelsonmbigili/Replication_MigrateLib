from mako.template import Template
from mako.lookup import TemplateLookup


class Template:
    def __init__(self, paths):
        self.lookup = TemplateLookup(
            directories=paths,
            input_encoding='utf-8',
            output_encoding='utf-8',
        )

    def load(self, params, filename=None):
        filename = filename or 'def.txt'
        template = self.lookup.get_template(filename)
        return template.render(**params)
