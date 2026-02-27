from libmig.metrics.migloc import file_mig_loc


def test_file_mig_loc():
    content_1 = """
from Cheetah import Template

def load_config():
    TEMPL_PATH = "templates/config.txt"
    values = {
        "VALUE": "5",
        "ROOT": "${ROOT}",
    }
    tmpl_file = open(TMPL_PATH).read()
    tmpl = Template.Template(
        tmpl_file, 
        searchList=[values]
    )    
    pxe_config = str(tmpl)
    return pxe_config
"""
    content_2 = """
from jinja2 import Envirinment, FileSystemLoader

def load_config():
    TEMPL_PATH = "templates/config.txt"
    values = {
        "VALUE": "5",
        "ROOT": "{{ROOT}}",
    }
    path, file = os.path.split(TEMPL_PATH)
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)
    template = env.get_template(file)

    pxe_config = template.render(values)
    return pxe_config
"""

    loc = file_mig_loc(content_1, content_2)
    expected_loc = 16
    assert loc == expected_loc, f"Expected {expected_loc}, got {loc}"
