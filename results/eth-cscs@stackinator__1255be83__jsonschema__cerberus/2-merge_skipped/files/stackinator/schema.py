import json
import pathlib

from cerberus import Validator
import yaml

prefix = pathlib.Path(__file__).parent.resolve()

# create a validator that will insert optional fields with their default values
# if they have not been provided.


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        # if instance is none, it's not possible to set any default for any sub-property
        if instance is not None:
            for property, subschema in properties.items():
                if "default" in subschema:
                    instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            yield error

    return jsonschema.validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


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