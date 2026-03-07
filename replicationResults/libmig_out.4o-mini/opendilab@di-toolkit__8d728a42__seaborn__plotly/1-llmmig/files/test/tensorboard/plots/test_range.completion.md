### Explanation of Changes
To migrate the code from using the "seaborn" library to "plotly", the following changes were made:

1. **Importing Plotly**: The `seaborn` library was replaced with `plotly.graph_objects` for creating plots.
2. **Setting Up the Plot**: Instead of using `plt.figure()` and `plt.tight_layout()`, we create a `plotly.graph_objects.Figure` object directly.
3. **Creating the Plot**: The plotting function `tb_create_range_plots` needs to be modified to use Plotly's plotting methods. This involves creating traces and adding them to the figure.
4. **Saving the Plot**: The method to save the plot was changed from `plt.savefig()` to `plot.write_image()`.

The overall structure of the test remains the same, but the plotting logic is adapted to fit Plotly's API.

### Modified Code
```python
import matplotlib.pyplot as plt
import pytest
import plotly.graph_objects as go
from hbutils.testing import isolated_directory, disable_output

from ditk.tensorboard import tb_create_range_plots
from test.testing import get_testfile


@pytest.mark.unittest
class TestTensorboardPlotsRange:
    def test_tb_create_range_plots(self, image_diff):
        answer_file = get_testfile('pong_tb_plot.png')
        with isolated_directory({'pong_tb': get_testfile('pong_tb')}):
            # sns.set() is not needed for plotly
            fig = go.Figure()

            with disable_output():
                tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5,
                    fig=fig  # Assuming tb_create_range_plots can accept a figure object
                )

            # No need for plt.tight_layout() in plotly
            fig.write_image('plot.png', scale=2)  # Adjust scale as needed

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
```

### Note
The function `tb_create_range_plots` is assumed to be modified to accept a `fig` parameter for Plotly. If this function is not designed to work with Plotly, further modifications would be necessary to adapt its internal logic to create traces and add them to the Plotly figure.