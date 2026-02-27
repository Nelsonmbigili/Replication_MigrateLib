### Explanation of Changes:
The original code does not explicitly use the `tqdm` library, so there are no progress bars to migrate directly. However, if the intention is to replace `tqdm` with `alive-progress` for progress bar functionality, we need to identify where progress bars might be used in the context of the code. Since the provided code does not include any progress bar usage, no changes are necessary to migrate from `tqdm` to `alive-progress`.

If progress bars were used in other parts of the application (e.g., iterating over a loop with `tqdm`), the migration would involve:
1. Replacing `from tqdm import tqdm` with `from alive_progress import alive_bar`.
2. Replacing `tqdm` usage with `alive_bar` context managers.

Since no such usage exists in the provided code, no modifications are required. Below is the unchanged code:

### Modified Code:
```python
import pytest
from hbutils.testing import disable_output

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
            df = tb_extract_log(get_testfile('tb1', 'sac'))
        assert df['step'].min() == 1000
        assert df['step'].max() == 32980

        basic_eval_episode_return_mean = \
            df[~df['basic/eval_episode_return_mean'].isna()]['basic/eval_episode_return_mean']
        assert basic_eval_episode_return_mean.mean() == pytest.approx(-1130.8211126327515)
        assert basic_eval_episode_return_mean.std() == pytest.approx(479.9282245210739)

    def test_tb_extract_recursive_logs_tb1_sac(self):
        with disable_output():
            mapping = tb_extract_recursive_logs(get_testfile('tb1', 'sac'))
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
            mapping = tb_extract_recursive_logs(get_testfile('tb1'))
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

### Notes:
- The provided code does not use `tqdm` or any progress bar functionality, so no migration to `alive-progress` is necessary.
- If progress bars are used elsewhere in the application, the migration steps outlined above can be applied.