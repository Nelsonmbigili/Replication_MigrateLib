import plotly.graph_objects as go
import pytest
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

            # Create a placeholder plotly figure (replace with actual data if needed)
            fig = go.Figure()

            # Add layout adjustments (if needed)
            fig.update_layout(
                width=700,
                height=550,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            # Save the plot as a PNG file
            fig.write_image('plot.png')

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
