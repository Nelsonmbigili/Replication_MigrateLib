### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Session Mocking**: The `requests.Session` mock was replaced with `aiohttp.ClientSession` mock since `aiohttp` uses `ClientSession` for managing HTTP requests.
2. **Asynchronous Code**: `aiohttp` is an asynchronous library, so all functions interacting with `aiohttp` were updated to use `async def` and `await` for asynchronous calls.
3. **Mocking Asynchronous Methods**: Mocking was updated to handle asynchronous methods (`async def`) using `AsyncMock` from `unittest.mock`.
4. **HTTP Methods**: The `get` and `post` methods were updated to their `aiohttp` equivalents, which require `await` for execution.
5. **Response Handling**: `aiohttp` responses are handled differently. For example, `response.json()` and `response.content` are coroutines and need to be awaited.
6. **Fixtures**: The `mock_session` fixture was updated to mock `aiohttp.ClientSession` instead of `requests.Session`.

Below is the modified code:

---

### Modified Code
```python
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kling import ImageGen, VideoGen, BaseGen, call_for_daily_check, TaskStatus

import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock


@pytest.fixture
def mock_session():
    with patch("aiohttp.ClientSession", new_callable=AsyncMock) as mock:
        yield mock.return_value


@pytest.fixture
def base_gen(mock_session):
    return BaseGen("mock_cookie")


@pytest.fixture
def image_gen(mock_session):
    return ImageGen("mock_cookie")


@pytest.fixture
def video_gen(mock_session):
    return VideoGen("mock_cookie")


def test_base_gen_init(base_gen):
    assert isinstance(base_gen, BaseGen)
    assert base_gen.cookie == "mock_cookie"


def test_image_gen_init(image_gen):
    assert isinstance(image_gen, ImageGen)
    assert image_gen.cookie == "mock_cookie"


def test_video_gen_init(video_gen):
    assert isinstance(video_gen, VideoGen)
    assert video_gen.cookie == "mock_cookie"


def test_parse_cookie_string():
    cookie_string = "key1=value1; key2=value2; kuaishou_key=value3"
    cookiejar, is_cn = BaseGen.parse_cookie_string(cookie_string)
    assert is_cn == True
    assert dict(cookiejar) == {
        "key1": "value1",
        "key2": "value2",
        "kuaishou_key": "value3",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("gen_class", [ImageGen, VideoGen])
async def test_get_account_point(gen_class, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.get.return_value.__aenter__.return_value.json.side_effect = [
        {"status": 200},
        {"status": 200, "data": {"total": 1000}},
    ]
    assert await gen.get_account_point() == 10.0


@patch("builtins.open", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_image_uploader(mock_open, image_gen, mock_session):
    mock_open.return_value.__enter__.return_value.read.return_value = b"image_data"
    mock_session.get.return_value.__aenter__.return_value.json.side_effect = [
        {"status": 200, "data": {"token": "mock_token"}},
        {"result": 1},
        {"status": 200, "data": {"url": "mock_url"}},
    ]
    mock_session.post.return_value.__aenter__.return_value.json.side_effect = [
        {"result": 1},
        {"result": 1},
    ]

    result = await image_gen.image_uploader("mock_image_path")
    assert result == "mock_url"


@pytest.mark.asyncio
async def test_fetch_metadata(base_gen, mock_session):
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "data": {"status": 100, "key": "value"}
    }
    result, status = await base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 100, "key": "value"}
    assert status == TaskStatus.COMPLETED

    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "data": {"status": 50}
    }
    result, status = await base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 50}
    assert status == TaskStatus.FAILED

    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "data": {"status": 80}
    }
    result, status = await base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 80}
    assert status == TaskStatus.PENDING


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "gen_class,method_name", [(ImageGen, "get_images"), (VideoGen, "get_video")]
)
async def test_get_content(gen_class, method_name, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": {"task": {"id": "mock_id"}}
    }
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "data": {"status": 100, "works": [{"resource": {"resource": "mock_resource"}}]}
    }

    method = getattr(gen, method_name)
    result = await method("mock_prompt")
    assert result == ["mock_resource"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "gen_class,method_name", [(ImageGen, "save_images"), (VideoGen, "save_video")]
)
@patch("os.path.exists", return_value=False)
@patch("os.mkdir")
async def test_save_content(mock_mkdir, mock_exists, gen_class, method_name, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.post.return_value.__aenter__.return_value.json.return_value = {
        "data": {"task": {"id": "mock_id"}}
    }
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "data": {"status": 100, "works": [{"resource": {"resource": "mock_resource"}}]}
    }

    mock_session.get.return_value.__aenter__.return_value.status = 200

    with patch("builtins.open", new_callable=MagicMock):
        method = getattr(gen, method_name)
        await method("mock_prompt", "mock_output_dir")

    mock_mkdir.assert_called_once_with("mock_output_dir")


@pytest.mark.asyncio
async def test_call_for_daily_check():
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value.ok = True
    mock_session.get.return_value.__aenter__.return_value.json.return_value = {
        "status": "success"
    }

    result = await call_for_daily_check(mock_session, True)
    assert result == True

    mock_session.get.return_value.__aenter__.return_value.ok = False
    with pytest.raises(Exception):
        await call_for_daily_check(mock_session, False)


if __name__ == "__main__":
    pytest.main()
```

---

### Key Notes:
- All `requests`-specific code was replaced with `aiohttp` equivalents.
- The `pytest.mark.asyncio` decorator was added to test asynchronous functions.
- Mocking was updated to handle asynchronous methods using `AsyncMock`.
- The `await` keyword was used for all `aiohttp` methods and response handling.