### Explanation of Changes:
To migrate from the `toml` library (version 0.10.2) to the `tomli` library (version 2.2.1), the following changes were made:
1. **Library Import**: Replaced the `import toml` statement with `import tomli`.
2. **Functionality Adjustments**:
   - The `tomli` library only supports reading TOML files or strings, not writing. This is fine since the original code only uses `toml` for reading.
   - Updated the `toml.loads` and `toml.load` calls to their `tomli` equivalents:
     - `toml.loads` → `tomli.loads`
     - `toml.load` → `tomli.load`
   - Adjusted the exception handling to ensure compatibility with `tomli`.

### Modified Code:
```python
import logging
import os
import pathlib

import tomli
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
                d.update(tomli.loads(r))
            except TypeError:  # to read files
                try:
                    d.update(tomli.load(r))
                except TypeError:  # to read streams
                    d.update(r)
        except Exception as e:
            raise ConfigParserError(e)

    return d
```

### Summary of Changes:
- Replaced `import toml` with `import tomli`.
- Updated `toml.loads` to `tomli.loads`.
- Updated `toml.load` to `tomli.load`.
- No other changes were made to preserve the original structure and functionality of the code.