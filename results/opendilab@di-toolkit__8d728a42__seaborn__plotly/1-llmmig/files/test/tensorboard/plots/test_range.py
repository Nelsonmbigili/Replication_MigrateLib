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
            with disable_output():
                # Generate data for plotting
                data = tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            # Create a Plotly figure
            fig = go.Figure()

            # Assuming `data` contains x and y values for the plot
            # Replace 'x' and 'y' with the actual keys from the `data` object
            fig.add_trace(go.Scatter(x=data['x'], y=data['y'], mode='lines', name='Reward Mean'))

            # Set layout properties
            fig.update_layout(
                width=700,
                height=550,
                margin=dict(l=50, r=50, t=50, b=50),
                title="Tensorboard Range Plot",
                xaxis_title="Step",
                yaxis_title="Reward Mean"
            )

            # Save the plot as an image
            fig.write_image('plot.png')

            # Compare the generated image with the answer file
            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
