### Explanation of Changes
To migrate the code from using the `toml` library to the `tomli` library, the following changes were made:

1. **Import Statement**: The import statement for `toml` was changed to `tomli`.
2. **Function Calls**: The `tomli` library does not have a `load` function that accepts a string directly. Instead, it requires a file-like object for the `load` function. Therefore, the code was modified to use `tomli.loads` for string input and `tomli.load` for file-like objects.
3. **Error Handling**: The error handling structure was retained, but the specific calls to `toml` were updated to reflect the new `tomli` usage.

### Modified Code
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
                    with open(r, 'rb') as f:  # Open the file in binary mode
                        d.update(tomli.load(f))
                except TypeError:  # to read streams
                    d.update(r)
        except Exception as e:
            raise ConfigParserError(e)

    return d
```