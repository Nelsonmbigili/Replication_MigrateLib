from libmig.utils.file_diff import FileDiff


def test_run():
    a = """
from pathlib import Path
from subprocess import Popen, PIPE
from typing import IO
""".strip()

    b = """
from pathlib import Path
from typing import Optional
""".strip()

    diff = FileDiff(a, b)

    assert diff.removed == [2, 3]
    assert diff.added == [2]
