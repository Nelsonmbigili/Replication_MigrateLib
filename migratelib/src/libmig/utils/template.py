class Template:
    def __init__(self, template: str):
        self.template = template.strip()

    def render(self, variables: dict):
        rendered = self.template
        for name, value in variables.items():
            rendered = rendered.replace(f"<{name}>", str(value))

        return rendered
