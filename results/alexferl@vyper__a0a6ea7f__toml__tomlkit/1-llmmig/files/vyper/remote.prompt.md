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
from distconfig import Proxy
import toml
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
            return toml.loads

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