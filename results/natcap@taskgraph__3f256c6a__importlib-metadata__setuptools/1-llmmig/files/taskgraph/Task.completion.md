### Explanation of Changes:
To migrate the code from using the `importlib-metadata` library to using the `setuptools` library for retrieving package version information, the following changes were made:
1. **Replaced `importlib.metadata` imports**:
   - Removed the `try` block that imports `PackageNotFoundError` and `version` from `importlib.metadata` or `importlib_metadata`.
   - Instead, imported `pkg_resources` from `setuptools` to handle package version retrieval.
   
2. **Updated version retrieval logic**:
   - Replaced the `version('taskgraph')` call with `pkg_resources.get_distribution('taskgraph').version`.
   - Replaced the `PackageNotFoundError` exception with `pkg_resources.DistributionNotFound` to handle cases where the package is not installed.

3. **Removed compatibility logic for `importlib-metadata`**:
   - Removed the fallback logic for Python versions earlier than 3.8, as `setuptools` is compatible across all Python versions supported by the application.

### Modified Code:
Here is the updated code after migrating to `setuptools`:

```python
"""Task graph framework."""
import collections
import hashlib
import inspect
import logging
import logging.handlers
import multiprocessing
import multiprocessing.pool
import os
import pathlib
import pickle
import pprint
import queue
import sqlite3
import threading
import time

import pkg_resources  # Import from setuptools for version handling

import retrying

try:
    __version__ = pkg_resources.get_distribution('taskgraph').version
except pkg_resources.DistributionNotFound:
    # package is not installed; no metadata available
    pass


_VALID_PATH_TYPES = (str, pathlib.PurePath)
_TASKGRAPH_DATABASE_FILENAME = 'taskgraph_data.db'

try:
    import psutil
    HAS_PSUTIL = True
    if psutil.WINDOWS:
        # Windows' scheduler doesn't use POSIX niceness.
        PROCESS_LOW_PRIORITY = psutil.BELOW_NORMAL_PRIORITY_CLASS
    else:
        # On POSIX, use system niceness.
        # -20 is high priority, 0 is normal priority, 19 is low priority.
        # 10 here is an arbitrary selection that's probably nice enough.
        PROCESS_LOW_PRIORITY = 10
except ImportError:
    HAS_PSUTIL = False

LOGGER = logging.getLogger(__name__)
_MAX_TIMEOUT = 5.0  # amount of time to wait for threads to terminate


# We want our processing pool to be nondeamonic so that workers could use
# multiprocessing if desired (deamonic processes cannot start new processes)
# the following bit of code to do this was taken from
# https://stackoverflow.com/a/8963618/42897
class NoDaemonProcess(multiprocessing.Process):
    """Make 'daemon' attribute always return False."""

    @property
    def daemon(self):
        """Return False indicating not a daemon process."""
        return False

    @daemon.setter
    def daemon(self, value):
        """Do not allow daemon value to be overriden."""
        pass


class NoDaemonContext(type(multiprocessing.get_context('spawn'))):
    """From https://stackoverflow.com/a/8963618/42897.

    "As the current implementation of multiprocessing [3.7+] has been
    extensively refactored to be based on contexts, we need to provide a
    NoDaemonContext class that has our NoDaemonProcess as attribute.
    [NonDaemonicPool] will then use that context instead of the default
    one." "spawn" is chosen as default since that is the default and only
    context option for Windows and is the default option for Mac OS as
    well since 3.8.

    """

    Process = NoDaemonProcess


class NonDaemonicPool(multiprocessing.pool.Pool):
    """NonDaemonic Process Pool."""

    def __init__(self, *args, **kwargs):
        """Invoke super to set the context of Pool class explicitly."""
        kwargs['context'] = NoDaemonContext()
        super(NonDaemonicPool, self).__init__(*args, **kwargs)


def _null_func():
    """Use when func=None on add_task."""
    return None


def _initialize_logging_to_queue(logging_queue):
    """Add a synchronized queue to a new process.

    This is intended to be called as an initialization function to
    ``multiprocessing.Pool`` to establish logging from a Pool worker to the
    main python process via a multiprocessing Queue.

    Args:
        logging_queue (multiprocessing.Queue): The queue to use for passing
            log records back to the main process.

    Returns:
        None

    """
    root_logger = logging.getLogger()

    # By the time this function is called, `root_logger` has a copy of all of
    # the logging handlers registered to it within the parent process, which
    # leads to duplicate logging in some cases.  By removing all of the
    # handlers here, we ensure that log messages can only be passed back to the
    # parent process by the `logging_queue`, where they will be handled.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(logging.NOTSET)
    handler = logging.handlers.QueueHandler(logging_queue)
    root_logger.addHandler(handler)


def _logging_queue_monitor(logging_queue):
    """Monitor ``logging_queue`` for message and pass to ``logger``."""
    LOGGER.debug('Starting logging worker')
    while True:
        record = logging_queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)
    LOGGER.debug('_logging_queue_monitor shutting down')


def _create_taskgraph_table_schema(taskgraph_database_path):
    """Create database exists and/or ensures it is compatible and recreate.

    Args:
        taskgraph_database_path (str): path to an existing database or desired
            location of a new database.

    Returns:
        None.

    """
    sql_create_projects_table_script = (
        """
        CREATE TABLE taskgraph_data (
            task_reexecution_hash TEXT NOT NULL,
            target_path_stats BLOB NOT NULL,
            result BLOB NOT NULL,
            PRIMARY KEY (task_reexecution_hash)
        );
        CREATE TABLE global_variables (
            key TEXT NOT NULL,
            value BLOB,
            PRIMARY KEY (key)
        );
        """)

    table_valid = True
    expected_table_column_name_map = {
        'taskgraph_data': [
            'task_reexecution_hash', 'target_path_stats', 'result'],
        'global_variables': ['key', 'value']}
    if os.path.exists(taskgraph_database_path):
        try:
            # check that the tables exist and the column names are as expected
            for expected_table_name in expected_table_column_name_map:
                table_result = _execute_sqlite(
                    '''
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table' AND name=?
                    ''', taskgraph_database_path,
                    argument_list=[expected_table_name],
                    mode='read_only', execute='execute', fetch='all')
                if not table_result:
                    raise ValueError(f'missing table {expected_table_name}')

                # this query returns a list of results of the form
                # [(0, 'task_reexecution_hash', 'TEXT', 1, None, 1), ... ]
                # we'll just check that the header names are the same, no
                # need to be super aggressive, also need to construct the
                # PRAGMA string directly since it doesn't take arguments
                table_info_result = _execute_sqlite(
                    f'PRAGMA table_info({expected_table_name})',
                    taskgraph_database_path, mode='read_only',
                    execute='execute', fetch='all')

                expected_column_names = expected_table_column_name_map[
                    expected_table_name]
                header_count = 0
                for header_line in table_info_result:
                    column_name = header_line[1]
                    if column_name not in expected_column_names:
                        raise ValueError(
                            f'expected {column_name} in table '
                            f'{expected_table_name} but not found')
                    header_count += 1
                if header_count < len(expected_column_names):
                    raise ValueError(
                        f'found only {header_count} of an expected '
                        f'{len(expected_column_names)} columns in table '
                        f'{expected_table_name}')
                if not table_info_result:
                    raise ValueError(f'missing table {expected_table_name}')
        except Exception:
            # catch all "Exception"s because anything that goes wrong while
            # checking the database should be considered a bad database and we
            # should make a new one.
            LOGGER.exception(
                f'{taskgraph_database_path} exists, but is incompatible '
                'somehow. Deleting and making a new one.')
            os.remove(taskgraph_database_path)
            table_valid = False
    else:
        # table does not exist
        table_valid = False

    if not table_valid:
        # create the base table
        _execute_sqlite(
            sql_create_projects_table_script, taskgraph_database_path,
            mode='modify', execute='script')
        # set the database version
        _execute_sqlite(
            '''
            INSERT OR REPLACE INTO global_variables
            VALUES ("version", ?)
            ''', taskgraph_database_path, mode='modify',
            argument_list=(__version__,))
```

### Summary:
The migration involved replacing `importlib-metadata` with `setuptools` for package version handling. The rest of the code remains unchanged.