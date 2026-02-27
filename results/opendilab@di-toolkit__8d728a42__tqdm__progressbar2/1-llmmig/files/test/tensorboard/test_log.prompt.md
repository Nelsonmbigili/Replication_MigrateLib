The following Python code currently uses the library "tqdm" version 4.67.1.
Migrate this code to use the library "progressbar2" version 4.5.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tqdm" to "progressbar2".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tqdm" and "progressbar2".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
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