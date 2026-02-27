import glob
import io
import os
import shutil
import sys
from pathlib import Path
from typing import Any
from typing import cast as _cast

import pytest
import plac
from test_base import replace_stdin
from test_base import replace_stdout

from hexrec.cli import main as cli_main
from hexrec.xxd import ZERO_BLOCK_SIZE
from hexrec.xxd import parse_seek
from hexrec.xxd import xxd_core


@pytest.fixture
def tmppath(tmpdir):
    return Path(str(tmpdir))


@pytest.fixture(scope='module')
def datadir(request):
    dir_path, _ = os.path.splitext(request.module.__file__)
    assert os.path.isdir(str(dir_path))
    return dir_path


@pytest.fixture
def datapath(datadir):
    return Path(str(datadir))


def read_text(path):
    path = str(path)
    with open(path, 'rt') as file:
        data = file.read()
    data = data.replace('\r\n', '\n').replace('\r', '\n')  # normalize
    return data


def read_bytes(path):
    path = str(path)
    with open(path, 'rb') as file:
        data = file.read()
    return data


def normalize_whitespace(text):
    return ' '.join(text.split())


def test_normalize_whitespace():
    ans_ref = 'abc def'
    ans_out = normalize_whitespace('abc\tdef')
    assert ans_ref == ans_out


def test_parse_seek():
    assert parse_seek(None) == ('', 0)


def test_by_filename_text(tmppath, datapath):
    prefix = 'test_xxd_'
    test_filenames = glob.glob(str(datapath / (prefix + '*.c')))
    test_filenames += glob.glob(str(datapath / (prefix + '*.hexstr')))
    test_filenames += glob.glob(str(datapath / (prefix + '*.mot')))
    test_filenames += glob.glob(str(datapath / (prefix + '*.xxd')))

    for filename in test_filenames:
        filename = os.path.basename(filename)
        print('@', filename, file=sys.stderr)
        path_out = tmppath / filename
        path_ref = datapath / filename

        cmdline = filename[len(prefix):].replace('_', ' ')
        args = cmdline.split()
        path_in = datapath / os.path.splitext(args[-1])[0]
        args = ['xxd'] + args[:-1] + [str(path_in), str(path_out)]

        result = plac.Interpreter.call(cli_main, args)
        assert result == 0

        ans_out = read_text(path_out)
        ans_ref = read_text(path_ref)
        # if ans_out != ans_ref: raise AssertionError(str(path_ref))
        assert ans_out == ans_ref


def test_by_filename_bytes(tmppath, datapath):
    copy_filenames = [
        (r'xxd.1', r'test_xxd_-r_xxd.1.patch.xxd.bin'),
    ]
    for path_ref, path_out in copy_filenames:
        path_ref = str(datapath / path_ref)
        path_out = str(tmppath / path_out)
        shutil.copy(path_ref, path_out)

    prefix = 'test_xxd_'
    test_filenames = glob.glob(str(datapath / (prefix + '*.bin')))

    for filename in test_filenames:
        filename = os.path.basename(filename)
        print('@', filename, file=sys.stderr)
        path_out = tmppath / filename
        path_ref = datapath / filename

        cmdline = filename[len(prefix):].replace('_', ' ')
        args = cmdline.split()
        path_in = datapath / os.path.splitext(args[-1])[0]
        args = ['xxd'] + args[:-1] + [str(path_in), str(path_out)]

        result = plac.Interpreter.call(cli_main, args)
        assert result == 0

        ans_out = read_bytes(path_out)
        ans_ref = read_bytes(path_ref)
        # if ans_out != ans_ref: raise AssertionError(str(path_ref))
        assert ans_out == ans_ref


def test_xxd_include_stdin_cli(tmppath, datapath):
    filename = 'xxd_-i_STDIN_file.c'
    path_out = tmppath / filename
    path_ref = datapath / filename
    path_in = datapath / 'file'

    args = 'xxd -i -'.split() + [str(path_out)]

    data_in = read_bytes(path_in)
    with replace_stdin(io.BytesIO(data_in)):
        result = plac.Interpreter.call(cli_main, args)
    assert result == 0

    ans_out = read_text(path_out)
    ans_ref = read_text(path_ref)
    assert ans_out == ans_ref
