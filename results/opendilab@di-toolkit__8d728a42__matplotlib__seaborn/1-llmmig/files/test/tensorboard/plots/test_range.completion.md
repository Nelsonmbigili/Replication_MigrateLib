### Explanation of Changes:
To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:
1. **Figure Creation**: Instead of using `plt.figure()` from `matplotlib`, `seaborn` automatically handles figure creation when plotting. The explicit call to `plt.figure()` was removed.
2. **Plot Styling**: The `sns.set()` call remains, as it is already part of `seaborn` and sets the default style for plots.
3. **Tight Layout**: The `plt.tight_layout()` call was removed because `seaborn` automatically adjusts layouts for its plots.
4. **Saving the Plot**: The `plt.savefig()` call was replaced with `sns.despine()` (to remove unnecessary spines) and `plt.savefig()` was retained for saving the plot, as `seaborn` does not have a direct save function.

### Modified Code:
```python
import matplotlib.pyplot as plt
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
            sns.set()  # Set seaborn style

            with disable_output():
                tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            sns.despine()  # Remove unnecessary spines
            plt.savefig('plot.png', bbox_inches='tight')

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
```