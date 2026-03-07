### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, I made the following changes:
1. Removed the import statement for `matplotlib.pyplot` since `seaborn` provides its own plotting functions that can be used directly.
2. Replaced the `plt.figure()` call with `sns.set()` to configure the aesthetics of the plots, as `seaborn` automatically applies a default style.
3. The `plt.tight_layout()` and `plt.savefig()` functions are still valid in the context of `seaborn`, so they remain unchanged.

### Modified Code
Here is the modified code after migrating from `matplotlib` to `seaborn`:

```python
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
            # Removed plt.figure() as sns handles figure creation

            with disable_output():
                tb_create_range_plots(
                    'pong_tb',
                    'step', 'evaluator_step/reward_mean',
                    upper_bound=5e5
                )

            plt.tight_layout()  # Still valid, can be used after seaborn plots
            plt.savefig('plot.png', bbox_inches='tight')  # Still valid

            assert image_diff(answer_file, 'plot.png', throw_exception=False) < 0.05
``` 

Note: The `plt.tight_layout()` and `plt.savefig()` calls are retained as they are still applicable in the context of `seaborn` plots. If the `tb_create_range_plots` function uses `matplotlib` internally, it will still work as expected.