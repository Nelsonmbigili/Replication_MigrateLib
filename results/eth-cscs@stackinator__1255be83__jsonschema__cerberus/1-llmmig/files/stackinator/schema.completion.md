### Explanation of Changes

The original code uses the `jsonschema` library to validate JSON data against a schema and to set default values for missing fields. To migrate this code to use the `cerberus` library, the following changes were made:

1. **Schema Definition**: `cerberus` uses a different schema format compared to `jsonschema`. The schemas in the original code (loaded from JSON files) need to be rewritten in the `cerberus` format. This step assumes that the schemas are converted manually or through a tool outside the provided code.

2. **Default Value Handling**: In `cerberus`, default values can be specified directly in the schema using the `default` keyword. The library automatically sets default values for missing fields during validation, so the custom `extend_with_default` function is no longer needed.

3. **Validation**: The `cerberus.Validator` class is used to validate data against the schema. Unlike `jsonschema`, `cerberus` does not require extending the validator for default value handling.

4. **Schema Loading**: The schemas are now assumed to be in `cerberus` format and loaded as Python dictionaries instead of JSON files.

5. **Validation Logic**: The `cerberus` validator is instantiated and used to validate data. The `validate` method is used to check if the data conforms to the schema, and it also applies default values.

### Modified Code

```python
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
```

### Key Notes:
1. The schemas (`config_schema`, `compilers_schema`, etc.) must now be in the `cerberus` format. This migration assumes that the schemas have been converted outside the provided code.
2. The `extend_with_default` function is removed because `cerberus` handles default values natively.
3. The `Validator` class from `cerberus` is used to validate data and apply default values.

This code is now fully migrated to use the `cerberus` library version 1.3.7.