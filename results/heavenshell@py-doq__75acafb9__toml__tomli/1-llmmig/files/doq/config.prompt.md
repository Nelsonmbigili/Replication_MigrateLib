The following Python code currently uses the library "toml" version 0.10.2.
Migrate this code to use the library "tomli" version 2.2.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "toml" to "tomli".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "toml" and "tomli".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import os
from configparser import ConfigParser as SafeConfigParser


PROJECT_CONFIGS = ('setup.cfg', 'pyproject.toml')


def read_setup_cfg(filepath):
    try:
        config = SafeConfigParser()
        config.read(filepath)
        return config
    except Exception:
        pass
    return None


def read_pyproject_toml(filepath):
    import toml

    with open(filepath) as f:
        config = toml.load(f)

    if config.get('tool', {}).get('doq') is None:
        return None

    return config.get('tool').get('doq')


def get_config_from_setup_cfg(configs, args):
    defaults = {}
    current_args = vars(args)
    for key in current_args.keys():
        if type(getattr(args, key)).__name__ == 'bool':
            value = configs['doq'].getboolean(key)
            if value is not None:
                defaults[key] = value
                continue

        value = configs['doq'].get(key)
        if value is not None:
            defaults[key] = value

    return defaults


def find_config_path():
    # Check current directory.
    for config_file in PROJECT_CONFIGS:
        if os.path.isfile(config_file):
            yield os.path.abspath(config_file)

    # Check parent directory
    current_dir = os.getcwd()
    while os.path.abspath(os.path.join(current_dir, '..')):
        # Walrus operator can use since Python 3.8
        # We support Python 3.7.
        basepath = os.path.abspath(os.path.join(current_dir, '..'))
        for config_file in PROJECT_CONFIGS:
            if os.path.isfile(os.path.join(basepath, config_file)):
                yield os.path.abspath(os.path.join(basepath, config_file))
        break


def find_config(args):
    """Find config.

    If `config` is not given, search setup.cfg and pyproject.toml.

    :param args:
    """
    defaults = {}
    paths = [os.path.abspath(args.config)] if args.config else find_config_path()
    for filepath in paths:
        if filepath.endswith('setup.cfg'):
            configs = read_setup_cfg(filepath)
            if not configs.has_section('doq'):
                continue

            defaults = get_config_from_setup_cfg(configs, args)
            break

        if filepath.endswith('pyproject.toml'):
            defaults = read_pyproject_toml(filepath)
            if not defaults:
                continue

            break

    return defaults

```