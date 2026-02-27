### Explanation of Changes:
To migrate the code from using `seaborn` to `altair`, the following changes were made:
1. **Removed `sns.set()`**: Seaborn's `set()` function is used to configure the aesthetics of plots. Altair does not require this, as it uses a declarative approach to define visualizations.
2. **Replaced `matplotlib.pyplot` with Altair's declarative plotting**: Altair does not use `matplotlib` for rendering plots. Instead, it generates visualizations using a JSON-based grammar of graphics. The `tb_create_range_plots` function's output is assumed to be data that can be visualized using Altair.
3. **Replaced `plt.figure`, `plt.tight_layout`, and `plt.savefig`**: Altair visualizations are saved using the `save` method, which supports formats like PNG, SVG, and HTML. The `alt.Chart` object is used to define and render the plot.

### Modified Code:
```python
import altair as alt
import pytest
from hbutils.testing import isolated_directory, disable_output

from ditk.tensorboard import tb_create_range_plots
from test.testing import get_testfile


@pytest.mark.unittest
class TestTensorboardPlotsRange:
    def test_tb_create_range_plots(self, image_diff):
        answer_file = get_testfile('pong_tb_plot.png')
        with isolated_directory({'pong_tb': get_testfile('pong_tb')}):
            with disable_output():
                # Assuming tb_create_range_plots returns a DataFrame or similar data structure
                data = tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            # Create the Altair chart
            chart = alt.Chart(data).mark_line().encode(
                x='step:Q',
                y='evaluator_step/reward_mean:Q'
            ).properties(
                width=700,
                height=550
            )

            # Save the chart as a PNG file
            chart.save('plot.png')

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
```

### Key Notes:
- The `tb_create_range_plots` function is assumed to return a data structure (e.g., a Pandas DataFrame) that can be directly used with Altair. If this assumption is incorrect, additional modifications may be needed to adapt the data for Altair.
- The `alt.Chart` object is used to define the visualization, with `mark_line()` specifying a line chart and `encode()` mapping the data fields to the x and y axes.
- The `chart.save()` method is used to save the visualization as a PNG file, replacing `plt.savefig`.