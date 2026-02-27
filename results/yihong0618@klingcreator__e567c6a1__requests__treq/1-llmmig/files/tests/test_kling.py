import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from twisted.internet.defer import inlineCallbacks
import treq

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kling import ImageGen, VideoGen, BaseGen, call_for_daily_check, TaskStatus


@pytest.fixture
def mock_session():
    with patch("treq.get") as mock_get, patch("treq.post") as mock_post:
        yield {"get": mock_get, "post": mock_post}


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
@inlineCallbacks
def test_get_account_point(gen_class, mock_session):
    gen = gen_class("mock_cookie")
    mock_session["get"].side_effect = [
        MagicMock(json_content=MagicMock(return_value={"status": 200})),
        MagicMock(json_content=MagicMock(return_value={"status": 200, "data": {"total": 1000}})),
    ]
    result = yield gen.get_account_point()
    assert result == 10.0


@patch("builtins.open", new_callable=MagicMock)
@inlineCallbacks
def test_image_uploader(mock_open, image_gen, mock_session):
    mock_open.return_value.__enter__.return_value.read.return_value = b"image_data"
    mock_session["get"].side_effect = [
        MagicMock(json_content=MagicMock(return_value={"status": 200, "data": {"token": "mock_token"}})),
        MagicMock(json_content=MagicMock(return_value={"result": 1})),
        MagicMock(json_content=MagicMock(return_value={"status": 200, "data": {"url": "mock_url"}})),
    ]
    mock_session["post"].side_effect = [
        MagicMock(json_content=MagicMock(return_value={"result": 1})),
        MagicMock(json_content=MagicMock(return_value={"result": 1})),
    ]

    result = yield image_gen.image_uploader("mock_image_path")
    assert result == "mock_url"


@inlineCallbacks
def test_fetch_metadata(base_gen, mock_session):
    mock_session["get"].return_value = MagicMock(
        json_content=MagicMock(return_value={"data": {"status": 100, "key": "value"}})
    )
    result, status = yield base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 100, "key": "value"}
    assert status == TaskStatus.COMPLETED

    mock_session["get"].return_value = MagicMock(
        json_content=MagicMock(return_value={"data": {"status": 50}})
    )
    result, status = yield base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 50}
    assert status == TaskStatus.FAILED

    mock_session["get"].return_value = MagicMock(
        json_content=MagicMock(return_value={"data": {"status": 80}})
    )
    result, status = yield base_gen.fetch_metadata("mock_task_id")
    assert result == {"status": 80}
    assert status == TaskStatus.PENDING


@pytest.mark.parametrize(
    "gen_class,method_name", [(ImageGen, "get_images"), (VideoGen, "get_video")]
)
@inlineCallbacks
def test_get_content(gen_class, method_name, mock_session):
    gen = gen_class("mock_cookie")
    mock_session["post"].return_value = MagicMock(
        json_content=MagicMock(return_value={"data": {"task": {"id": "mock_id"}}})
    )
    mock_session["get"].return_value = MagicMock(
        json_content=MagicMock(
            return_value={
                "data": {"status": 100, "works": [{"resource": {"resource": "mock_resource"}}]}
            }
        )
    )

    method = getattr(gen, method_name)
    result = yield method("mock_prompt")
    assert result == ["mock_resource"]


# Other tests follow the same pattern: replacing `requests` with `treq` and handling async calls.
