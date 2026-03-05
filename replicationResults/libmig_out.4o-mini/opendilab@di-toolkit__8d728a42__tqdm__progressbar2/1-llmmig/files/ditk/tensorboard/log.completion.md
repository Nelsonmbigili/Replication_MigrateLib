### Explanation of Changes
To migrate the code from using the `tqdm` library to the `progressbar2` library, I made the following changes:

1. **Import Statement**: Changed the import from `tqdm.auto` to `progressbar`.
2. **Progress Bar Initialization**: Replaced the `tqdm` progress bar initialization with `progressbar.ProgressBar()`.
3. **Iteration with Progress Bar**: Adjusted the way the progress bar is updated during iteration. In `progressbar2`, the progress bar needs to be updated manually using the `update()` method.

The overall structure of the code remains unchanged, and the functionality is preserved.

### Modified Code
```python
import os
from typing import Dict

import pandas as pd
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator, SCALARS
from progressbar import ProgressBar


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

    total_events = sum(len(event_acc.Scalars(tag)) for tag in event_acc.Tags()['scalars'])
    progress = ProgressBar(max_value=total_events)
    current_event = 0

    for tag, scalar_event in _yields():
        progress.update(current_event)
        progress.message = f'{shown_name} --> {tag} #{scalar_event.step}'
        current_event += 1
        
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
    total_dirs = sum(1 for _ in os.walk(root_log_dir))
    progress = ProgressBar(max_value=total_dirs)
    current_dir_index = 0

    for current_dir, subdirs, subfiles in os.walk(root_log_dir):
        cdir = os.path.relpath(current_dir, root_log_dir)
        progress.update(current_dir_index)
        progress.message = cdir
        current_dir_index += 1
        
        event_acc = _init_acc_from_dir(current_dir)
        if _exist_check_with_event_acc(event_acc):
            retval[cdir] = _extract_with_event_acc(event_acc, cdir)

    return retval
```