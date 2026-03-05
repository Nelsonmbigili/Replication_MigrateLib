### Explanation of Changes
To migrate the code from using `matplotlib` to `altair`, the following changes were made:

1. **Import Statement**: The import for `matplotlib.pyplot` was removed and replaced with an import for `altair`.
2. **Plotting Functions**: The plotting functions were replaced with `altair` equivalents. Instead of creating a figure and saving it, we create a chart using `altair`'s `Chart` class and specify the encoding and mark type.
3. **Saving the Plot**: Instead of using `plt.savefig`, we use `chart.save` to save the plot in the desired format.
4. **Data Handling**: The data passed to the plotting function needs to be structured in a way that `altair` can understand, typically as a DataFrame.

Here is the modified code:

```python
import altair as alt
import pytest
import pandas as pd
import seaborn as sns
from hbutils.testing import isolated_directory, disable_output

from ditk.tensorboard import tb_create_range_plots
from test.testing import get_testfile


@pytest.mark.unittest
class TestTensorboardPlotsRange:
    def test_tb_create_range_plots(self, image_diff):
        answer_file = get_testfile('pong_tb_plot.png')
        with isolated_directory({'pong_tb': get_testfile('pong_tb')}):
            sns.set()

            with disable_output():
                tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            # Assuming tb_create_range_plots returns a DataFrame
            data = tb_create_range_plots(
                'pong_tb',
                'step', 'evaluator_step/reward_mean',
                upper_bound=5e5
            )

            chart = alt.Chart(data).mark_line().encode(
                x='step:Q',
                y='evaluator_step/reward_mean:Q'
            ).properties(
                width=700,
                height=550
            )

            chart.save('plot.png')

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
```

### Note
- The code assumes that `tb_create_range_plots` can return a DataFrame suitable for `altair`. If it does not, additional modifications would be necessary to ensure the data is in the correct format for plotting.