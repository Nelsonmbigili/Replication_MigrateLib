### Explanation of Changes
To migrate from the `python-dotenv` library to the `environs` library, the primary change involves replacing the `load_dotenv()` function with the `environs` library's approach to loading environment variables. The `environs` library automatically loads environment variables from a `.env` file when you create an instance of the `Env` class. Therefore, we will import `Env` from `environs` and instantiate it to load the environment variables.

### Modified Code
```python
from environs import Env

env = Env()
env.read_env()

```