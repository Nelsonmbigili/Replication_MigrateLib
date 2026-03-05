### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several changes were necessary:

1. **Session Management**: The `requests.Session` object was replaced with `pycurl.Curl`. The `pycurl` library does not have a session concept like `requests`, so each request is handled individually using `Curl` objects.

2. **Making Requests**: The `get` and `post` methods from `requests` were replaced with `setopt` calls to configure the `Curl` object for GET and POST requests. The URL, headers, and other options are set using `setopt`.

3. **Handling Responses**: The response handling is different in `pycurl`. Instead of calling `.json()` on the response, we need to capture the response data using a callback function and then parse it manually (e.g., using `json.loads`).

4. **Error Handling**: The error handling for HTTP responses is also different. We need to check the HTTP response code using `getinfo` after executing the request.

5. **Mocking**: The mocking of the session in tests was adjusted to accommodate the new `pycurl` usage.

Here is the modified code:

```python
import sys
import os
import pycurl
import json
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kling import ImageGen, VideoGen, BaseGen, call_for_daily_check, TaskStatus

import pytest
from unittest.mock import patch, MagicMock, mock_open


@pytest.fixture
def mock_session():
    class MockCurl:
        def __init__(self):
            self.response_buffer = BytesIO()
            self.url = ""
            self.headers = []
            self.post_data = None
            self.response_code = 200

        def setopt(self, option, value):
            if option == pycurl.URL:
                self.url = value
            elif option == pycurl.WRITEFUNCTION:
                self.write_function = value
            elif option == pycurl.HTTPHEADER:
                self.headers = value
            elif option == pycurl.POSTFIELDS:
                self.post_data = value

        def perform(self):
            # Simulate a response based on the URL and post data
            if "mock_url" in self.url:
                self.response_buffer.write(b'{"status": 200, "data": {"token": "mock_token"}}')
            elif "mock_image_path" in self.url:
                self.response_buffer.write(b'{"result": 1}')
            else:
                self.response_buffer.write(b'{"status": 200, "data": {"url": "mock_url"}}')

            self.response_buffer.seek(0)

        def getinfo(self, option):
            if option == pycurl.RESPONSE_CODE:
                return self.response_code

        def close(self):
            pass

    with patch("pycurl.Curl", new_callable=MockCurl) as mock:
        yield mock


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


@pytest.mark.parametrize("gen_class", [ImageGen, VideoGen])
def test_get_account_point(gen_class, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.perform()
    assert gen.get_account_point() == 10.0


@patch("builtins.open", new_callable=MagicMock)
def test_image_uploader(mock_open, image_gen, mock_session):
    mock_open.return_value.__enter__.return_value.read.return_value = b"image_data"
    mock_session.perform()
    result = image_gen.image_uploader("mock_image_path")
    assert result == "mock_url"


def test_fetch_metadata(base_gen, mock_session):
    mock_session.perform()
    result, status = base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 200, "data": {"key": "value"}}
    assert status == TaskStatus.COMPLETED

    mock_session.perform()
    result, status = base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 50}
    assert status == TaskStatus.FAILED

    mock_session.perform()
    result, status = base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 80}
    assert status == TaskStatus.PENDING


@pytest.mark.parametrize(
    "gen_class,method_name", [(ImageGen, "get_images"), (VideoGen, "get_video")]
)
def test_get_content(gen_class, method_name, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.perform()
    method = getattr(gen, method_name)
    result = method("mock_prompt")
    assert result == ["mock_resource"]


@pytest.mark.parametrize(
    "gen_class,method_name", [(ImageGen, "save_images"), (VideoGen, "save_video")]
)
@patch("os.path.exists", return_value=False)
@patch("os.mkdir")
def test_save_content(mock_mkdir, mock_exists, gen_class, method_name, mock_session):
    gen = gen_class("mock_cookie")
    mock_session.perform()

    with patch("builtins.open", new_callable=MagicMock):
        method = getattr(gen, method_name)
        method("mock_prompt", "mock_output_dir")

    mock_mkdir.assert_called_once_with("mock_output_dir")


def test_call_for_daily_check():
    mock_session = MagicMock()
    mock_session.perform()
    result = call_for_daily_check(mock_session, True)
    assert result == True

    mock_session.perform()
    with pytest.raises(Exception):
        call_for_daily_check(mock_session, False)


@patch("builtins.open", new_callable=mock_open, read_data=b"mock_image_data")
@patch.object(VideoGen, "image_uploader", return_value="mock_image_url")
def test_video_gen_get_video(mock_uploader, mock_file, video_gen, mock_session):
    mock_session.perform()
    result = video_gen.get_video("mock_prompt")
    assert result == ["mock_video_url"]

    result = video_gen.get_video("mock_prompt", image_path="mock_image.jpg")
    assert result == ["mock_video_url"]

    result = video_gen.get_video("mock_prompt", image_url="http://mock.com/image.jpg")
    assert result == ["mock_video_url"]

    result = video_gen.get_video("mock_prompt", is_high_quality=True)
    assert result == ["mock_video_url"]


@patch("os.path.exists", return_value=False)
@patch("os.mkdir")
@patch("builtins.open", new_callable=mock_open)
def test_video_gen_save_video(
    mock_file, mock_mkdir, mock_exists, video_gen, mock_session
):
    mock_session.perform()

    video_gen.save_video("mock_prompt", "mock_output_dir")

    mock_mkdir.assert_called_once_with("mock_output_dir")
    mock_file.assert_called_once_with("mock_output_dir/0.mp4", "wb")
    mock_file().write.assert_called_once_with(b"mock_video_content")


@patch("builtins.open", new_callable=mock_open, read_data=b"mock_image_data")
@patch.object(ImageGen, "image_uploader", return_value="mock_image_url")
def test_image_gen_get_images(mock_uploader, mock_file, image_gen, mock_session):
    mock_session.perform()
    result = image_gen.get_images("mock_prompt")
    assert result == ["mock_image_url"]

    result = image_gen.get_images("mock_prompt", image_path="mock_image.jpg")
    assert result == ["mock_image_url"]

    result = image_gen.get_images("mock_prompt", image_url="http://mock.com/image.jpg")
    assert result == ["mock_image_url"]


@patch("os.path.exists", return_value=False)
@patch("os.mkdir")
@patch("builtins.open", new_callable=mock_open)
@patch("threading.Thread")
def test_image_gen_save_images(
    mock_thread, mock_file, mock_mkdir, mock_exists, image_gen, mock_session
):
    mock_session.perform()

    image_gen.save_images("mock_prompt", "mock_output_dir")

    mock_mkdir.assert_called_once_with("mock_output_dir")
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()
    mock_thread.return_value.join.assert_called_once()


@patch.object(VideoGen, "fetch_metadata")
def test_extend_video_completed(mock_fetch_metadata, video_gen):
    mock_fetch_metadata.return_value = (
        {"works": [{"resource": {"resource": "mock_resource"}}]},
        TaskStatus.COMPLETED,
    )

    result = video_gen.extend_video(123, "mock_prompt")

    assert result == ["mock_resource"]


@patch.object(VideoGen, "fetch_metadata")
def test_extend_video_pending(mock_fetch_metadata, video_gen):
    mock_fetch_metadata.return_value = (
        {"works": []},
        TaskStatus.PENDING,
    )

    with pytest.raises(Exception):
        video_gen.extend_video(123, "mock_prompt")


@patch.object(VideoGen, "fetch_metadata")
def test_extend_video_failed(mock_fetch_metadata, video_gen):
    mock_fetch_metadata.return_value = (
        {"works": []},
        TaskStatus.FAILED,
    )

    with pytest.raises(Exception):
        video_gen.extend_video(123, "mock_prompt")


@patch.object(VideoGen, "fetch_metadata")
def test_extend_video_no_works(mock_fetch_metadata, video_gen):
    mock_fetch_metadata.return_value = (
        {},
        TaskStatus.COMPLETED,
    )

    with pytest.raises(Exception):
        video_gen.extend_video(123, "mock_prompt")


if __name__ == "__main__":
    pytest.main()
``` 

This code now uses `pycurl` for HTTP requests instead of `requests`, while maintaining the original structure and functionality of the tests.