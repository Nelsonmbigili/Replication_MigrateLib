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
