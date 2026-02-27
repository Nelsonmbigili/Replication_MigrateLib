The following Python code currently uses the library "urllib3" version 2.2.1.
Migrate this code to use the library "aiohttp" version 3.11.16 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "urllib3" to "aiohttp".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "urllib3" and "aiohttp".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
class Waits:
    def __init__(self, driver):
        response = driver.command_executor._request(
            "GET",
            f"{driver.command_executor._url}/session/{driver.session_id}/timeouts",
        )
        self.implicit = int(response["value"]["implicit"] / 1000)
        self.page_load = int(response["value"]["pageLoad"] / 1000)
        self.script = int(response["value"]["script"] / 1000)


def get_implicit_wait(driver):
    response = driver.command_executor._request(
        "GET", f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
    )
    return int(response["value"]["implicit"] / 1000)

```