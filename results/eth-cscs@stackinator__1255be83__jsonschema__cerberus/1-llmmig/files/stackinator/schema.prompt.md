The following Python code currently uses the library "jsonschema" version 4.23.0.
Migrate this code to use the library "cerberus" version 1.3.7 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "jsonschema" to "cerberus".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "jsonschema" and "cerberus".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import json
import pathlib

import jsonschema
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


validator = extend_with_default(jsonschema.Draft7Validator)

# load recipe yaml schema
config_schema = json.load(open(prefix / "schema/config.json"))
config_validator = validator(config_schema)
compilers_schema = json.load(open(prefix / "schema/compilers.json"))
compilers_validator = validator(compilers_schema)
environments_schema = json.load(open(prefix / "schema/environments.json"))
environments_validator = validator(environments_schema)
cache_schema = json.load(open(prefix / "schema/cache.json"))
cache_validator = validator(cache_schema)

```