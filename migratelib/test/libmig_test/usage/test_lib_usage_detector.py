from pathlib import Path

from libmig.usage.lib_usage_detector import LibUsageDetector


def test_detect_lib_usage__single_statement():
    code_path = Path("test/test_data/usage/scenario_1")
    assert len(LibUsageDetector(code_path, [], ["requests"]).detect()) == 2
    assert len(LibUsageDetector(code_path, [], ["httpx"]).detect()) == 1


def test_detect_lib_usage__multiple_statements():
    code_path = Path("test/test_data/usage/scenario_1")
    usages = LibUsageDetector(code_path, [], ["aiohttp"]).detect()
    assert len(usages) == 3
    usage_1 = [u for u in usages if u.file == "code_1.py" and u.line == 2][0]
    usage_2 = [u for u in usages if u.file == "code_1.py" and u.line == 3][0]
    usage_3 = [u for u in usages if u.file == "a_dir/code_2.py"][0]

    assert usage_1.api == "aiohttp"
    assert usage_1.char == 7

    assert usage_2.api == "aiohttp.ClientSession"
    assert usage_2.char == 20

    assert usage_3.api == "aiohttp"
    assert usage_3.char == 24


def test_detect_lib_usage__multiple_import_names():
    code_path = Path("test/test_data/usage/scenario_1")
    assert len(LibUsageDetector(code_path, [], ["setuptools"]).detect()) == 1


def test_detect_lib_usage__exclude():
    code_path = Path("test/test_data/usage/scenario_1")
    ex = ["a_dir"]
    assert len(LibUsageDetector(code_path, exclude_dirs=ex, import_names=["requests"]).detect()) == 1
    assert len(LibUsageDetector(code_path, exclude_dirs=ex, import_names=["httpx"]).detect()) == 1
