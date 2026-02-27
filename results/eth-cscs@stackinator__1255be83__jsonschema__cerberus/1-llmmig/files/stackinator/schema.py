import json
import pathlib

from cerberus import Validator
import yaml

prefix = pathlib.Path(__file__).parent.resolve()


def py2yaml(data, indent):
    dump = yaml.dump(data)
    lines = [ln for ln in dump.split("\n") if ln != ""]
    res = ("\n" + " " * indent).join(lines)
    return res


# Load recipe YAML schemas (converted to Cerberus format)
with open(prefix / "schema/config.json") as f:
    config_schema = json.load(f)
with open(prefix / "schema/compilers.json") as f:
    compilers_schema = json.load(f)
with open(prefix / "schema/environments.json") as f:
    environments_schema = json.load(f)
with open(prefix / "schema/cache.json") as f:
    cache_schema = json.load(f)

# Create Cerberus validators
config_validator = Validator(config_schema)
compilers_validator = Validator(compilers_schema)
environments_validator = Validator(environments_schema)
cache_validator = Validator(cache_schema)

# Example usage of validators (if needed)
# data = {...}  # Some data to validate
# if config_validator.validate(data):
#     validated_data = config_validator.document  # Data with defaults applied
# else:
#     print("Validation errors:", config_validator.errors)
