### Explanation of Changes
To migrate the code from using the `seaborn` library to the `altair` library, several key changes were made:

1. **Import Statements**: The import of `seaborn` and `matplotlib.pyplot` was removed, as `altair` will be used for plotting.
2. **Plotting with Altair**: The plotting logic was replaced with `altair` syntax. Instead of creating a figure and using `plt.savefig`, we create a `Chart` object in `altair` and save it using the `save` method.
3. **Data Handling**: The data passed to `tb_create_range_plots` needs to be structured in a way that `altair` can understand, typically as a DataFrame. This may require additional adjustments depending on the data format.

Here is the modified code:

```python
import pytest
import altair as alt
import pandas as pd
from hbutils.testing import isolated_directory, disable_output

from ditk.tensorboard import tb_create_range_plots
from test.testing import get_testfile


@pytest.mark.unittest
class TestTensorboardPlotsRange:
    def test_tb_create_range_plots(self, image_diff):
        answer_file = get_testfile('pong_tb_plot.png')
        with isolated_directory({'pong_tb': get_testfile('pong_tb')}):
            # Prepare data for Altair
            data = tb_create_range_plots(
                'pong_tb',
                'step', 'evaluator_step/reward_mean',
                upper_bound=5e5
            )

            # Create Altair chart
            chart = alt.Chart(data).mark_line().encode(
                x='step:Q',
                y='evaluator_step/reward_mean:Q'
            ).properties(
                width=700,
                height=550
            )

            # Save the chart
            chart.save('plot.png')

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
```

### Note
- The `tb_create_range_plots` function is assumed to return a DataFrame suitable for `altair`. If it does not, you may need to adjust how the data is prepared before creating the chart.
- The `mark_line()` method is used to create a line chart, which is a common visualization type. Adjust the encoding and properties as necessary to match the original intent of the seaborn plot.