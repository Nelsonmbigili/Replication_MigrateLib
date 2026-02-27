import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import contextmanager
from copy import deepcopy
from functools import partial
from io import StringIO
from unittest.mock import patch

import pyperclip
from jmespath import compile as jcompile
from jsonpath_ng import parse as jparse
from rich.console import Console
from rich.syntax import Syntax

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from jsonfmt import jsonfmt

JSON_FILE = f'{BASE_DIR}/test/example.json'
with open(JSON_FILE) as json_fp:
    JSON_TEXT = json_fp.read()

TOML_FILE = f'{BASE_DIR}/test/example.toml'
with open(TOML_FILE) as toml_fp:
    TOML_TEXT = toml_fp.read()

XML_FILE = f'{BASE_DIR}/test/example.xml'
with open(XML_FILE) as xml_fp:
    XML_TEXT = xml_fp.read()

YAML_FILE = f'{BASE_DIR}/test/example.yaml'
with open(YAML_FILE) as yaml_fp:
    YAML_TEXT = yaml_fp.read()

console = Console()

def color(text, fmt):
    """Highlight text using rich's Syntax class."""
    syntax_map = {
        'json': 'json',
        'toml': 'toml',
        'xml': 'xml',
        'yaml': 'yaml',
    }
    if fmt not in syntax_map:
        raise ValueError(f"Unsupported format: {fmt}")
    syntax = Syntax(text, syntax_map[fmt], theme="monokai", word_wrap=True)
    return console.render_str(syntax)


class FakeStream(StringIO):

    def __init__(self, initial_value='', newline='\n', tty=True):
        super().__init__(initial_value, newline)
        self._istty = tty

    def isatty(self):
        return self._istty

    def read(self):
        self.seek(0)
        content = super().read()

        self.seek(0)
        self.truncate()
        return content


class StdIn(FakeStream):
    name = '<stdin>'

    def fileno(self) -> int:
        return 0


class StdOut(FakeStream):
    name = '<stdout>'

    def fileno(self) -> int:
        return 1


class StdErr(FakeStream):
    name = '<stderr>'

    def fileno(self) -> int:
        return 2


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.py_obj = json.loads(JSON_TEXT)

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_is_clipboard_available(self):
        available = jsonfmt.is_clipboard_available()
        self.assertIsInstance(available, bool)

    def test_parse_querypath(self):
        jmespath, jsonpath = 'actions.name', '$..name'
        # test parse jmespath
        res1 = jsonfmt.parse_querypath(jmespath, None)
        res2 = jsonfmt.parse_querypath(jmespath, 'jmespath')

        self.assertEqual(res1, res2)
        # test parse jsonpath
        res3 = jsonfmt.parse_querypath(jsonpath, None)
        res4 = jsonfmt.parse_querypath(jsonpath, 'jsonpath')
        self.assertEqual(res3, res4)

        # test wrong args
        self.assertEqual(jsonfmt.parse_querypath(None, None), None)
        with self.assertRaises(SystemExit):
            jsonfmt.parse_querypath('as*df', None)

        with self.assertRaises(SystemExit):
            jsonfmt.parse_querypath(jsonpath, 'wrong')

    def test_parse_to_pyobj_with_jmespath(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, jcompile("actions[:].calorie"))
        self.assertEqual(matched_obj, ([1294.9, -2375, -420.5], 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jcompile("actions[*].name"))
        self.assertEqual(matched_obj, (['eating', 'sporting', 'sleeping'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jcompile("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27', '2023-05-15'], 'yaml'))
        # test not exists key
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jcompile("not_exist_key"))
        self.assertEqual(matched_obj, (None, 'toml'))
        # test index out of range
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jcompile('actions[7]'))
        self.assertEqual(matched_obj, (None, 'yaml'))

    def test_parse_to_pyobj_with_jsonpath(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, jparse("age"))
        self.assertEqual(matched_obj, (23, 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jparse("$..name"))
        self.assertEqual(matched_obj, (['Bob', 'eating', 'sporting', 'sleeping'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jparse("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27', '2023-05-15'], 'yaml'))
        # test not exists key
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jparse("not_exist_key"))
        self.assertEqual(matched_obj, (None, 'toml'))
        # test index out of range
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jparse('actions[7]'))
        self.assertEqual(matched_obj, (None, 'yaml'))

    def test_parse_to_pyobj_with_wrong_fmt(self):
        with self.assertRaises(jsonfmt.FormatError), open(__file__) as fp:
            jsonfmt.parse_to_pyobj(fp.read(), jcompile("actions[0].calorie"))

    # Other test cases remain unchanged...

if __name__ == "__main__":
    unittest.main()
