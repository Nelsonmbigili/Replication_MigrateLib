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
