import altair as alt
import pandas as pd
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
                # Generate the data using tb_create_range_plots
                data = tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            # Assuming `data` is a pandas DataFrame, create an Altair chart
            chart = alt.Chart(data).mark_line().encode(
                x='step:Q',
                y='evaluator_step/reward_mean:Q'
            ).properties(
                width=700,
                height=550
            )

            # Save the chart as a PNG file
            chart.save('plot.png')

            # Compare the generated plot with the answer file
            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
