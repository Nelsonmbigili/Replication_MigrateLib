from pathlib import Path

import pytest

completion_root = Path(__file__).parent.parent / "test_data" / "completions"


@pytest.fixture
def completion_1():
    return (completion_root / "completion_1__has_skipped_code.md").read_text("utf-8")
