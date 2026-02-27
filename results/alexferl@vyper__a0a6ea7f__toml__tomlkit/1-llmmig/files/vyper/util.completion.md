### Explanation of Changes
To migrate the code from using the `toml` library to `tomlkit`, the following changes were made:
1. **Import Statement**: Replaced the `import toml` statement with `import tomlkit`.
2. **Parsing TOML Strings**: Replaced `toml.loads(r)` with `tomlkit.parse(r)` to parse TOML strings.
3. **Loading TOML Files**: Replaced `toml.load(r)` with `tomlkit.load(r)` to load TOML data from a file-like object.
4. **Error Handling**: The `tomlkit` library has similar behavior to `toml` for exceptions, so no changes were needed for exception handling.

Below is the modified code:

---

### Modified Code
```python
import logging
import os
import pathlib

import tomlkit
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
                d.update(tomlkit.parse(r))  # Parse TOML string
            except TypeError:  # to read files
                try:
                    d.update(tomlkit.load(r))  # Load TOML from file-like object
                except TypeError:  # to read streams
                    d.update(r)
        except Exception as e:
            raise ConfigParserError(e)

    return d
```

---

### Summary of Changes
- Replaced `toml.loads` with `tomlkit.parse`.
- Replaced `toml.load` with `tomlkit.load`.
- No other changes were made to the code structure or logic.