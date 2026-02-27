### Explanation of Changes:
The original code uses `urllib3`'s `pyopenssl` module to inject and extract OpenSSL functionality into/from `urllib3`. Since we are migrating to `httpx`, which does not require such injection or extraction mechanisms, the `inject_into_urllib3` and `extract_from_urllib3` functions are no longer relevant. `httpx` uses `httpcore` under the hood for HTTP functionality and handles SSL/TLS natively without requiring manual injection.

The modified code removes the `inject_into_urllib3` and `extract_from_urllib3` logic entirely, as it is unnecessary in `httpx`. The `pytest` fixture is also removed because it was specifically tied to the `urllib3` injection process.

### Modified Code:
```python
import pytest
```