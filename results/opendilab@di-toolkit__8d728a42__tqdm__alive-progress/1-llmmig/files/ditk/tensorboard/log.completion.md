### Explanation of Changes:
To migrate the code from using the `tqdm` library to the `alive-progress` library:
1. Replaced `tqdm` imports with `alive-progress` imports.
2. Replaced `tqdm` progress bar initialization (`tqdm(...)`) with `alive_bar` context managers.
3. Used `bar()` method of `alive_bar` to iterate over items, replacing the direct iteration over `tqdm` objects.
4. Replaced `progress.set_description(...)` with `bar.title = ...` to update the progress bar title dynamically.

### Modified Code:
```python
import os
from typing import Dict

import pandas as pd
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator, SCALARS
from alive_progress import alive_bar


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

    with alive_bar(len(list(_yields())), title=f'{shown_name}') as bar:
        for tag, scalar_event in _yields():
            bar.title = f'{shown_name} --> {tag} #{scalar_event.step}'
            bar()  # Update the progress bar
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
    walk_items = list(os.walk(root_log_dir))
    with alive_bar(len(walk_items), title="Processing directories") as bar:
        for current_dir, subdirs, subfiles in walk_items:
            cdir = os.path.relpath(current_dir, root_log_dir)
            bar.title = cdir
            bar()  # Update the progress bar
            event_acc = _init_acc_from_dir(current_dir)
            if _exist_check_with_event_acc(event_acc):
                retval[cdir] = _extract_with_event_acc(event_acc, cdir)

    return retval
```

### Key Points:
1. **`alive_bar` Context Manager**: The `alive_bar` context manager is used to create and manage progress bars. It automatically handles the progress bar lifecycle.
2. **Dynamic Titles**: The `bar.title` attribute is used to dynamically update the progress bar's title, replacing `progress.set_description(...)` from `tqdm`.
3. **Progress Updates**: The `bar()` method is called to update the progress bar after each iteration.

This ensures the code now uses `alive-progress` while maintaining the original functionality and structure.