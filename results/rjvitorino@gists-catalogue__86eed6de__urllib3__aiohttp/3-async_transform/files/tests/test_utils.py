from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from scripts.gist import Gist
from scripts.utils import (
    create_gist_index,
    fetch_gist_content,
    fetch_gists,
    format_date,
    generate_folder_name,
    save_gist_files,
    update_readme,
)

# Example data
example_gist_data = {
    "id": "1",
    "created_at": "2024-06-17T09:30:09Z",
    "updated_at": "2024-06-17T09:30:09Z",
    "description": "Test gist",
    "files": {
        "file1.py": {
            "filename": "file1.py",
            "raw_url": "https://gist.githubusercontent.com/rjvitorino/dfef5433066c061954d29d1b15202290/raw/54a0207aaf64e70e57a2063795b0a1c88a6b046c/file1.py",
            "language": "Python",
        }
    },
    "owner": {"login": "rjvitorino", "html_url": "https://github.com/rjvitorino"},
}

example_gist = Gist.from_dict(example_gist_data)
import pytest


@pytest.mark.asyncio
@patch("requests.get")
async def test_fetch_gists(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [example_gist_data]
    mock_get.return_value = mock_response
    gists = await fetch_gists()
    assert len(gists) == 1
    assert gists[0].id == "1"


@pytest.mark.asyncio
@patch("requests.get")
async def test_fetch_gist_content(mock_get):
    mock_response = MagicMock()
    mock_response.text = "print('Hello, world!')"
    mock_get.return_value = mock_response
    content = await fetch_gist_content(
        "https://gist.githubusercontent.com/rjvitorino/dfef5433066c061954d29d1b15202290/raw/54a0207aaf64e70e57a2063795b0a1c88a6b046c/file1.py"
    )
    assert content == "print('Hello, world!')"


def test_format_date():
    assert format_date("2024-06-17T09:30:09Z") == "2024-06-17"
    assert format_date("2024-06-17T09:30:09Z", "YYYYMMDD") == "20240617"


@pytest.mark.asyncio
async def test_generate_folder_name():
    folder_name = await generate_folder_name(example_gist)
    assert folder_name == "20240617-file1-gist"


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open)
@patch("scripts.utils.fetch_gist_content")
async def test_save_gist_files(mock_fetch_content, mock_file):
    mock_fetch_content.return_value = "print('Hello, world!')"
    await save_gist_files(example_gist)
    mock_file.assert_called_with(Path("gists/20240617-file1-gist/files/file1.py"), "w")
    mock_file().write.assert_called_with("print('Hello, world!')")


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open)
async def test_create_gist_index(mock_file):
    await create_gist_index(example_gist)
    mock_file.assert_called_with(Path("gists/20240617-file1-gist/index.md"), "w")
    # Adjust the assertion to match the actual content
    calls = mock_file().write.call_args_list
    assert any(call[0][0].startswith("# 20240617-file1-gist") for call in calls)


@pytest.mark.asyncio
@patch("builtins.open", new_callable=mock_open)
async def test_update_readme(mock_file):
    await update_readme([example_gist])
    mock_file.assert_called_with(Path("README.md"), "w")
    # Adjust the assertion to match the actual content
    calls = mock_file().write.call_args_list
    assert any("## Gists" in call[0][0] for call in calls)
