from mako.lookup import TemplateLookup


class Template:
    def __init__(self, paths):
        self.lookup = TemplateLookup(
            directories=paths,
            module_directory=None,
            collection_size=500,
        )

    def load(self, params, filename=None):
        filename = filename or 'def.txt'
        template = self.lookup.get_template(filename)
        return template.render(**params)
