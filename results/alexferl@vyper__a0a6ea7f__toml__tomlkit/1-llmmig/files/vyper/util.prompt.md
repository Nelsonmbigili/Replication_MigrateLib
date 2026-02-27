The following Python code currently uses the library "toml" version 0.10.2.
Migrate this code to use the library "tomlkit" version 0.13.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "toml" to "tomlkit".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "toml" and "tomlkit".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import logging
import os
import pathlib

import toml
import yaml

try:
    import ujson as json
except ImportError:
    import json

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError

log = logging.getLogger("vyper.util")


class ConfigParserError(Exception):
    """Denotes failing to parse configuration file."""

    def __init__(self, message, *args):
        self.message = message
        super(ConfigParserError, self).__init__(message, *args)

    def __str__(self):
        return "While parsing config: {0}".format(self.message)


def abs_pathify(in_path):
    log.info("Trying to resolve absolute path to {0}".format(in_path))

    try:
        return pathlib.Path(in_path).resolve()
    except FileNotFoundError as e:
        log.error('Couldn"t discover absolute path: {0}'.format(e))
        return ""


def exists(path):
    try:
        os.stat(str(path))
        return True
    except FileNotFoundError:
        return False


def unmarshall_config_reader(r, d, config_type):
    config_type = config_type.lower()

    if config_type in ["yaml", "yml"]:
        try:
            f = yaml.safe_load(r)
            try:
                d.update(yaml.safe_load(f))
            except AttributeError:  # to read files
                d.update(f)
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == "json":
        try:
            f = json.loads(r)
            d.update(f)
        except Exception as e:
            raise ConfigParserError(e)

    elif config_type == "toml":
        try:
            try:
                d.update(toml.loads(r))
            except TypeError:  # to read files
                try:
                    d.update(toml.load(r))
                except TypeError:  # to read streams
                    d.update(r)
        except Exception as e:
            raise ConfigParserError(e)

    return d

```