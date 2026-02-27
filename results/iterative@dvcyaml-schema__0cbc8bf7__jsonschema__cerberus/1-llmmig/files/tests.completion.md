### Explanation of Changes:
To migrate the code from using the `jsonschema` library to the `cerberus` library, the following changes were made:
1. **Schema Validation**: The `jsonschema.validate` function was replaced with the `Validator` class from `cerberus`. The `Validator` class is used to validate data against a schema.
2. **Error Handling**: The `jsonschema.ValidationError` exception was replaced with the `Validator.errors` attribute, which contains validation errors in `cerberus`.
3. **Schema Format**: The `cerberus` library uses a slightly different schema format compared to `jsonschema`. If the schema in `schema.json` is in `jsonschema` format, it must be converted to the `cerberus` format. For simplicity, this code assumes the schema is already in `cerberus` format.
4. **Validation Logic**: The `Validator.validate` method is used to validate the data. If validation fails, the test asserts that errors exist.

Below is the modified code:

---

### Modified Code:
```python
#!/usr/bin/env python3
"""Tests for schema which runs validation using schema over examples folder."""
# pylint: disable=redefined-outer-name

import json
from pathlib import Path

from cerberus import Validator
import pytest
from ruamel.yaml import YAML

yaml = YAML(typ="safe")

root = Path(__file__).resolve().parent
examples_dir = root / "examples"
valid_dir = examples_dir / "valid"
invalid_dir = examples_dir / "invalid"


@pytest.fixture
def schema() -> dict:
    return json.loads((root / "schema.json").read_text(encoding="utf-8"))


def ids_gen(val: str) -> str:
    if not isinstance(val, Path):
        return str(val)
    if val.name.endswith(".dvc.yaml"):
        return val.name[:-9]
    return val.name


@pytest.mark.parametrize("example", valid_dir.iterdir(), ids=ids_gen)
def test_valid_examples(schema: dict, example: Path) -> None:
    validator = Validator(schema)
    data = yaml.load(example)
    assert validator.validate(data), f"Validation failed: {validator.errors}"


@pytest.mark.parametrize("example", invalid_dir.iterdir(), ids=ids_gen)
def test_invalid_examples(schema: dict, example: Path) -> None:
    validator = Validator(schema)
    data = yaml.load(example)
    assert not validator.validate(data), "Expected validation to fail, but it passed."
```

---

### Key Points:
1. The `Validator` class from `cerberus` is instantiated with the schema.
2. The `validate` method is used to check if the data conforms to the schema.
3. For valid examples, the test asserts that validation passes (`assert validator.validate(data)`).
4. For invalid examples, the test asserts that validation fails (`assert not validator.validate(data)`).
5. The `validator.errors` attribute is used to provide detailed error messages when validation fails.

This code assumes that the schema in `schema.json` is already in a format compatible with `cerberus`. If the schema is in `jsonschema` format, additional conversion would be required, which is outside the scope of this migration.