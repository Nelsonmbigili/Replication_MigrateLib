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
import os
from typing import Dict

import pandas as pd
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator, SCALARS
from tqdm.auto import tqdm


def _init_acc_from_dir(log_dir: str) -> EventAccumulator:
    event_acc = EventAccumulator(
        log_dir,
        size_guidance={SCALARS: 0},
    )
    event_acc.Reload()
    return event_acc


def _exist_check_with_event_acc(event_acc: EventAccumulator) -> bool:
    for tag in event_acc.Tags()['scalars']:
        for _ in event_acc.Scalars(tag):
            return True

    return False


def tb_has_log(log_dir: str) -> bool:
    event_acc = _init_acc_from_dir(log_dir)
    return _exist_check_with_event_acc(event_acc)


def _extract_with_event_acc(event_acc: EventAccumulator, shown_name: str):
    scalar_data = {}

    def _yields():
        for _tag in event_acc.Tags()['scalars']:
            for _event in event_acc.Scalars(_tag):
                yield _tag, _event

    progress = tqdm(_yields())
    for tag, scalar_event in progress:
        progress.set_description(f'{shown_name} --> {tag} #{scalar_event.step}')
        if scalar_event.step not in scalar_data:
            scalar_data[scalar_event.step] = {'step': scalar_event.step}
        scalar_data[scalar_event.step][tag] = scalar_event.value

    return pd.DataFrame(data=[
        item for _, item in
        sorted(scalar_data.items(), key=lambda x: x[0])
    ])


def tb_extract_log(log_dir: str) -> pd.DataFrame:
    event_acc = _init_acc_from_dir(log_dir)
    return _extract_with_event_acc(event_acc, log_dir)


def tb_extract_recursive_logs(root_log_dir: str) -> Dict[str, pd.DataFrame]:
    retval = {}
    progress = tqdm(os.walk(root_log_dir))
    for current_dir, subdirs, subfiles in progress:
        cdir = os.path.relpath(current_dir, root_log_dir)
        progress.set_description(cdir)
        event_acc = _init_acc_from_dir(current_dir)
        if _exist_check_with_event_acc(event_acc):
            retval[cdir] = _extract_with_event_acc(event_acc, cdir)

    return retval

```