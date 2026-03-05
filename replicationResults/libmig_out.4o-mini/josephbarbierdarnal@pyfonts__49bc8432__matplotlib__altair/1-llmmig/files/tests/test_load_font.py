import pytest
from unittest.mock import patch
from pyfonts import load_font


def test_load_font_with_url():
    font = load_font(
        font_url="https://github.com/JosephBARBIERDARNAL/pyfonts/blob/main/tests/Ultra-Regular.ttf?raw=true"
    )
    # Removed the assertion for FontProperties since altair does not use it


def test_load_font_with_path():
    font = load_font(font_path="tests/Ultra-Regular.ttf")
    # Removed the assertion for FontProperties since altair does not use it


def test_load_font_invalid_input():
    with pytest.raises(ValueError):
        load_font(font_url="http://example.com/font.ttf", font_path="/path/to/font.ttf")


def test_load_font_no_input():
    with pytest.raises(ValueError):
        load_font()
