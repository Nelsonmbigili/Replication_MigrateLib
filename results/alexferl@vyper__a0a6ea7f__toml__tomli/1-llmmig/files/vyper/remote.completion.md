### Explanation of Changes
To migrate from the `toml` library to the `tomli` library:
1. **Import Change**: Replaced the `import toml` statement with `import tomli`.
2. **Function Replacement**: The `toml.loads` function was replaced with `tomli.loads`. The `tomli` library provides a similar `loads` function for parsing TOML strings.
3. **Behavioral Note**: `tomli` is a read-only TOML parser, so it does not support writing TOML files. However, since the original code only uses `loads` for reading TOML, this limitation does not affect the migration.

### Modified Code
```python
from distconfig import Proxy
import tomli
import yaml

try:
    import ujson as json
except ImportError:
    import json

from . import constants, errors

PROVIDER_TYPE = {
    "consul": "distconfig.backends.consul.ConsulBackend",
    "etcd": "distconfig.backends.etcd.EtcdBackend",
    "zookeeper": "distconfig.backends.zookeeper.ZooKeeperBackend",
}


class RemoteProvider(object):
    def __init__(self, provider, client, path, v):
        self.v = v
        config_type = self.v._config_type
        if config_type != "" and config_type in constants.SUPPORTED_EXTENSIONS:
            self.config_type = config_type
        else:
            raise errors.UnsupportedConfigError(config_type)

        provider = PROVIDER_TYPE.get(provider)
        self.proxy = Proxy.configure(provider, client=client, parser=self._get_parser())

        self.config = self.proxy.get_config(path)

    @property
    def provider(self):
        return self.provider

    @property
    def client(self):
        return self.client

    @property
    def path(self):
        return self.path

    def _get_parser(self):
        if self.config_type == "json":
            return json.loads
        elif self.config_type in ["yaml", "yml"]:
            return yaml.safe_load
        elif self.config_type == "toml":
            return tomli.loads

    def get(self):
        d = {}
        for k, v in self.config.items():
            d[k] = v

        if self.config_type != "toml":
            return json.dumps(d)
        else:
            return d

    def add_listener(self, cb=None):
        if cb is not None:
            self.proxy.backend.add_listener(cb)
        else:
            self.proxy.backend.add_listener(self._update_kvstore)

    def _update_kvstore(self, e):
        self.v._kvstore = e
```

### Summary of Changes
- Replaced `import toml` with `import tomli`.
- Updated the `_get_parser` method to use `tomli.loads` instead of `toml.loads`.