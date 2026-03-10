### Explanation of Changes
To migrate from the `tqdm` library to the `alive-progress` library, the following changes were made:
1. **Import Statement**: The import statement for `tqdm` was removed, as it is no longer needed.
2. **Progress Bar Initialization**: The `tqdm` progress bar initialization and usage were replaced with `alive-progress` equivalents. The `alive-progress` library uses a different syntax for creating and updating progress bars.
3. **Context Management**: The context management for the progress bar was adjusted to fit the `alive-progress` style.

### Modified Code
Here is the modified code after migrating to `alive-progress`:

```python
import pytest
from hbutils.testing import disable_output
from alive_progress import alive_bar

from ditk.tensorboard import tb_has_log, tb_extract_log, tb_extract_recursive_logs
from test.testing import get_testfile


@pytest.mark.unittest
class TestTensorboardLog:
    @pytest.mark.parametrize(['segs', 'has_log'], [
        (('tb1',), False),
        (('tb1', 'sac'), True),
        (('tb1', 'td3'), True),
    ])
    def test_tb_has_log(self, segs, has_log):
        assert tb_has_log(get_testfile(*segs)) == has_log

    def test_tb_extract_log_tb1_sac(self):
        with disable_output():
            with alive_bar() as bar:
                df = tb_extract_log(get_testfile('tb1', 'sac'))
                bar()  # Update progress bar
        assert df['step'].min() == 1000
        assert df['step'].max() == 32980

        basic_eval_episode_return_mean = \
            df[~df['basic/eval_episode_return_mean'].isna()]['basic/eval_episode_return_mean']
        assert basic_eval_episode_return_mean.mean() == pytest.approx(-1130.8211126327515)
        assert basic_eval_episode_return_mean.std() == pytest.approx(479.9282245210739)

    def test_tb_extract_recursive_logs_tb1_sac(self):
        with disable_output():
            with alive_bar() as bar:
                mapping = tb_extract_recursive_logs(get_testfile('tb1', 'sac'))
                bar()  # Update progress bar
        assert isinstance(mapping, dict)
        assert sorted(mapping.keys()) == ['.']

        df = mapping['.']
        assert df['step'].min() == 1000
        assert df['step'].max() == 32980

        basic_eval_episode_return_mean = \
            df[~df['basic/eval_episode_return_mean'].isna()]['basic/eval_episode_return_mean']
        assert basic_eval_episode_return_mean.mean() == pytest.approx(-1130.8211126327515)
        assert basic_eval_episode_return_mean.std() == pytest.approx(479.9282245210739)

    def test_tb_extract_recursive_logs_tb1(self):
        with disable_output():
            with alive_bar() as bar:
                mapping = tb_extract_recursive_logs(get_testfile('tb1'))
                bar()  # Update progress bar
        assert isinstance(mapping, dict)
        assert sorted(mapping.keys()) == ['sac', 'td3']

        df_1 = mapping['sac']
        assert df_1['step'].min() == 1000
        assert df_1['step'].max() == 32980

        basic_eval_episode_return_mean = \
            df_1[~df_1['basic/eval_episode_return_mean'].isna()]['basic/eval_episode_return_mean']
        assert basic_eval_episode_return_mean.mean() == pytest.approx(-1130.8211126327515)
        assert basic_eval_episode_return_mean.std() == pytest.approx(479.9282245210739)

        df_2 = mapping['td3']
        assert df_2['step'].min() == 800
        assert df_2['step'].max() == 87152

        basic_eval_episode_return_mean = \
            df_2[~df_2['basic/eval_episode_return_mean'].isna()]['basic/eval_episode_return_mean']
        assert basic_eval_episode_return_mean.mean() == pytest.approx(-1125.0574578179253)
        assert basic_eval_episode_return_mean.std() == pytest.approx(318.2343800302068)
```

In this modified code, the `alive-progress` library is used to create a progress bar in a way that is compatible with the original code's structure and logic.