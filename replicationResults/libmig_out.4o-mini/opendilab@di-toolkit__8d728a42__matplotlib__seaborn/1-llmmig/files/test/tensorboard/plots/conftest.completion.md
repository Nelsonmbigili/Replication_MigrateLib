### Explanation of Changes
To migrate from "matplotlib" to "seaborn", the primary change involves replacing the `matplotlib.pyplot` import with `seaborn`. Since "seaborn" is built on top of "matplotlib", it can still utilize some of the same functionalities, but it provides a higher-level interface for creating attractive statistical graphics. In this case, the `plt.cla()` function, which clears the current axes, is not directly available in "seaborn". However, since "seaborn" does not have a direct equivalent for clearing plots, we can keep the `plt.cla()` call as it is, since it will still work with "seaborn".

### Modified Code
```python
import seaborn as sns
import pytest


@pytest.fixture(scope='module', autouse=True)
def clear_previous_plot():
    plt.cla()
```