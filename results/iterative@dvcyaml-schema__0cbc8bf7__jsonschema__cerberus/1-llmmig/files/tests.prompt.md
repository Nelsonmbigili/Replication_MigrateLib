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
#!/usr/bin/env python3
"""Tests for schema which runs validation using schema over examples folder."""
# pylint: disable=redefined-outer-name

import json
from pathlib import Path

import jsonschema
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
    jsonschema.validate(yaml.load(example), schema=schema)


@pytest.mark.parametrize("example", invalid_dir.iterdir(), ids=ids_gen)
def test_invalid_examples(schema: dict, example: Path) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(yaml.load(example), schema=schema)

```