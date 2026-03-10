import json
import pathlib

import cerberus
import yaml

prefix = pathlib.Path(__file__).parent.resolve()

# load recipe yaml schema
config_schema = json.load(open(prefix / "schema/config.json"))
config_validator = cerberus.Validator(config_schema)
compilers_schema = json.load(open(prefix / "schema/compilers.json"))
compilers_validator = cerberus.Validator(compilers_schema)
environments_schema = json.load(open(prefix / "schema/environments.json"))
environments_validator = cerberus.Validator(environments_schema)
cache_schema = json.load(open(prefix / "schema/cache.json"))
cache_validator = cerberus.Validator(cache_schema)

def py2yaml(data, indent):
    dump = yaml.dump(data)
    lines = [ln for ln in dump.split("\n") if ln != ""]
    res = ("\n" + " " * indent).join(lines)
    return res
