### Explanation of Changes:
To migrate from the `toml` library to `tomli`, the following changes were made:
1. **Import Statement**: Replaced the `import toml` statement with `import tomli`.
2. **File Reading**: The `tomli` library requires files to be opened in binary mode (`'rb'`) instead of text mode (`'r'`), as it expects a bytes-like object.
3. **Functionality**: The `tomli.load()` function is used in the same way as `toml.load()`, so no further changes were necessary.

### Modified Code:
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
    import tomli

    with open(filepath, 'rb') as f:  # Open the file in binary mode
        config = tomli.load(f)

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

### Summary of Changes:
- Replaced `import toml` with `import tomli`.
- Changed the file opening mode to `'rb'` in the `read_pyproject_toml` function to comply with `tomli`'s requirements.
- No other changes were made to ensure the code remains consistent with the original functionality.