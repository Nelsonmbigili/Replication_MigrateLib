import glob
import os
from pathlib import Path
from typing import cast as _cast, List

import pytest
import plac

from hexrec import IhexFile
from hexrec import SrecFile
from hexrec import __version__ as _version
from hexrec.cli import *

# Plac does not require explicit BaseCommand casting
main = _main  # suppress warnings


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


class TestSingleFileInOutCtxMgr:

    def test___init__(self):
        ctx = SingleFileInOutCtxMgr('in.mot', 'srec', 'out.hex', 'ihex', 33)
        assert ctx.input_path == 'in.mot'
        assert ctx.input_format == 'srec'
        assert ctx.output_path == 'out.hex'
        assert ctx.output_format == 'ihex'
        assert ctx.output_width == 33

    def test___init__no_out(self):
        ctx = SingleFileInOutCtxMgr('in.mot', 'srec', '', 'ihex', 33)
        assert ctx.input_path == 'in.mot'
        assert ctx.input_format == 'srec'
        assert ctx.output_path == 'in.mot'
        assert ctx.output_format == 'ihex'
        assert ctx.output_width == 33


class TestMultiFileInOutCtxMgr:

    def test___init__(self):
        ctx = MultiFileInOutCtxMgr(['in.mot'], ['srec'], 'out.hex', 'ihex', 33)
        assert ctx.input_paths == ['in.mot']
        assert ctx.input_formats == ['srec']
        assert ctx.output_path == 'out.hex'
        assert ctx.output_format == 'ihex'
        assert ctx.output_width == 33

    def test___init__no_out(self):
        ctx = MultiFileInOutCtxMgr(['in.mot'], ['srec'], '', 'ihex', 33)
        assert ctx.input_paths == ['in.mot']
        assert ctx.input_formats == ['srec']
        assert ctx.output_path == 'in.mot'
        assert ctx.output_format == 'ihex'
        assert ctx.output_width == 33


def test_main():
    try:
        plac.call(_main, ['__main__'])
    except SystemExit:
        pass


def test_guess_input_type():
    assert guess_input_type('x.mot') is SrecFile
    assert guess_input_type('-', 'ihex') is IhexFile
    assert guess_input_type('x.tek', 'ihex') is IhexFile

    match = 'standard input requires input format'
    with pytest.raises(ValueError, match=match):
        guess_input_type('-')


def test_guess_output_type():
    assert guess_output_type('y.mot') is SrecFile
    assert guess_output_type('-', 'ihex') is IhexFile
    assert guess_output_type('y.tek', 'ihex') is IhexFile


def test_missing_input_format():
    commands = ('clear', 'convert', 'crop', 'delete', 'fill', 'flood', 'merge',
                'shift')
    match = 'standard input requires input format'

    for command in commands:
        try:
            plac.call(_main, [command, '-', '-'])
        except ValueError as e:
            assert match in str(e)


def test_help():
    commands = ('clear', 'convert', 'crop', 'delete', 'fill', 'flood', 'merge',
                'shift', 'xxd')

    for command in commands:
        result = plac.call(_main, [command, '--help'])
        assert result is None  # plac prints help to stdout


def test_by_filename(tmppath, datapath):
    prefix = 'test_hexrec_'
    test_filenames: List[str] = glob.glob(str(datapath / (prefix + '*')))

    for filename in test_filenames:
        filename = os.path.basename(str(filename))
        path_out = str(tmppath / filename)
        path_ref = str(datapath / filename)

        cmdline = filename[len(prefix):].replace('_', ' ')
        args: List[str] = cmdline.split()
        path_in = str(datapath / args[-1])
        args = args[:-1] + [path_in, path_out]

        plac.call(_main, args)

        ans_out = read_text(path_out)
        ans_ref = read_text(path_ref)
        assert ans_out == ans_ref, filename


def test_fill_parse_byte_fail():
    try:
        plac.call(_main, 'fill -v 256 - -'.split())
    except ValueError as e:
        assert "invalid byte: '256'" in str(e)


def test_merge_nothing():
    result = plac.call(_main, 'merge -i raw -'.split())
    assert result is None  # plac does not return output


def test_merge_multi(datapath, tmppath):
    path_ins = [str(datapath / 'reversed.mot'),
                str(datapath / 'holes.mot')]
    path_out = str(tmppath / 'test_merge_multi.hex')
    args = ['merge'] + path_ins + [path_out]
    plac.call(_main, args)

    path_ref = str(datapath / 'merge_reversed_holes.hex')
    ans_out = read_text(path_out)
    ans_ref = read_text(path_ref)
    assert ans_out == ans_ref


def test_validate(datapath):
    path_in = str(datapath / 'bytes.mot')
    plac.call(_main, f'validate {path_in}'.split())


def test_srec_dummy(datapath):
    try:
        plac.call(_main, f'srec -h'.split())
    except SystemExit as e:
        assert e.code == 2


def test_srec_get_header_headless(datapath):
    path_in = str(datapath / 'headless.mot')
    plac.call(_main, f'srec get-header {path_in}'.split())


def test_srec_get_header_empty(datapath):
    path_in = str(datapath / 'bytes.mot')
    plac.call(_main, f'srec get-header {path_in}'.split())


def test_srec_get_header_ascii(datapath):
    path_in = str(datapath / 'header.mot')
    plac.call(_main, f'srec get-header -f ascii {path_in}'.split())


def test_srec_get_header_hex(datapath):
    path_in = str(datapath / 'header.mot')
    plac.call(_main, f'srec get-header -f hex {path_in}'.split())


def test_hexdump_version():
    expected = f'hexdump from Python hexrec {_version!s}'
    result = plac.call(_main, 'hexdump --version'.split())
    assert result is None  # plac does not return output


def test_hd_version():
    expected = f'hexdump from Python hexrec {_version!s}'
    result = plac.call(_main, 'hd --version'.split())
    assert result is None  # plac does not return output


def test_xxd_version():
    expected = f'{_version!s}'
    result = plac.call(_main, 'xxd --version'.split())
    assert result is None  # plac does not return output


def test_xxd_empty():
    result = plac.call(_main, 'xxd - -'.split())
    assert result is None  # plac does not return output


def test_xxd_parse_int_pass():
    result = plac.call(_main, 'xxd -c 0x10 - -'.split())
    assert result is None  # plac does not return output


def test_xxd_parse_int_fail():
    try:
        plac.call(_main, 'xxd -c ? - -'.split())
    except ValueError as e:
        assert "invalid integer: '?'" in str(e)
