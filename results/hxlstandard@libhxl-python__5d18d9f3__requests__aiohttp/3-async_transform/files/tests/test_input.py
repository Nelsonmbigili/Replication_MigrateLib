#coding=UTF8
"""
Unit tests for the hxl.input module
David Megginson
October 2014

License: Public Domain
"""

import unittest
import os
import sys
import io
import json
from urllib.error import HTTPError
from io import StringIO

import hxl
from hxl.input import make_input, HXLParseException, HXLReader, CSVInput, InputOptions


def _resolve_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)

DATA = [
   ['Sector', 'Organisation', 'Province name'],
   ['#sector', '#org', '#adm1'],
   ['WASH', 'Org A', 'Coast'],
   ['Health', 'Org B', 'Plains']
]

FILE_CSV = _resolve_file('./files/test_io/input-valid.csv')
FILE_CSV_HXL_EXT = _resolve_file('./files/test_io/input-valid.hxl')
FILE_CSV_UNTAGGED = _resolve_file('./files/test_io/input-untagged.csv')
FILE_TSV = _resolve_file('./files/test_io/input-valid.tsv')
FILE_SSV = _resolve_file('./files/test_io/input-valid.ssv')
FILE_ZIP_CSV = _resolve_file('./files/test_io/input-valid-csv.zip')
FILE_ZIP_CSV_UNTAGGED = _resolve_file('./files/test_io/input-untagged-csv.zip')
FILE_ZIP_INVALID = _resolve_file('./files/test_io/input-zip-invalid.zip')
FILE_CSV_LATIN1 = _resolve_file('./files/test_io/input-valid-latin1.csv')
FILE_CSV_OUT = _resolve_file('./files/test_io/output-valid.csv')
FILE_XLSX = _resolve_file('./files/test_io/input-valid.xlsx')
FILE_XLS = _resolve_file('./files/test_io/input-valid.xls')
FILE_XLSX_BROKEN = _resolve_file('./files/test_io/input-broken.xlsx')
FILE_XLSX_NOEXT = _resolve_file('./files/test_io/input-valid-xlsx.NOEXT')
FILE_XLSX_MERGED = _resolve_file('./files/test_io/input-merged.xlsx')
FILE_XLSX_INFO = _resolve_file('./files/test_io/input-quality.xlsx')
FILE_XLS_INFO = _resolve_file('./files/test_io/input-quality.xls')
FILE_JSON = _resolve_file('./files/test_io/input-valid.json')
FILE_JSON_TXT = _resolve_file('./files/test_io/input-valid-json.txt')
FILE_JSON_UNTAGGED = _resolve_file('./files/test_io/input-untagged.json')
FILE_JSON_OUT = _resolve_file('./files/test_io/output-valid.json')
FILE_JSON_OBJECTS = _resolve_file('./files/test_io/input-valid-objects.json')
FILE_JSON_OBJECTS_UNTAGGED = _resolve_file('./files/test_io/input-untagged-objects.json')
FILE_JSON_OBJECTS_OUT = _resolve_file('./files/test_io/output-valid-objects.json')
FILE_JSON_NESTED = _resolve_file('./files/test_io/input-valid-nested.json')
FILE_JSON_SELECTOR = _resolve_file('./files/test_io/input-valid-json-selector.json')
FILE_MULTILINE = _resolve_file('./files/test_io/input-multiline.csv')
FILE_FUZZY = _resolve_file('./files/test_io/input-fuzzy.csv')
FILE_INVALID = _resolve_file('./files/test_io/input-invalid.csv')
FILE_NOTAG1 = _resolve_file('./files/test_io/input-notag1.html')
FILE_NOTAG2 = _resolve_file('./files/test_io/input-notag2.html')
FILE_BINARY_INVALID = _resolve_file('./files/test_io/input-invalid.png')

URL_CSV = 'https://raw.githubusercontent.com/HXLStandard/libhxl-python/prod/tests/files/test_io/input-valid.csv'
URL_CSV_HXL_EXT = 'https://ourairports.com/countries/CA/airports.hxl'
URL_XLSX = 'https://raw.githubusercontent.com/HXLStandard/libhxl-python/prod/tests/files/test_io/input-valid.xlsx'
URL_XLS = 'https://raw.githubusercontent.com/HXLStandard/libhxl-python/prod/tests/files/test_io/input-valid.xls'
URL_JSON = 'https://raw.githubusercontent.com/HXLStandard/libhxl-python/prod/tests/files/test_io/input-valid.json'
URL_GOOGLE_SHEET_NOHASH = 'https://docs.google.com/spreadsheets/d/1VTswL-w9EI0IdGIBFZoZ-2RmIiebXKsrhv03yd7LlIg/edit'
URL_GOOGLE_SHEET_HASH = 'https://docs.google.com/spreadsheets/d/1VTswL-w9EI0IdGIBFZoZ-2RmIiebXKsrhv03yd7LlIg/edit#gid=299366282'
URL_GOOGLE_FILE = 'https://drive.google.com/file/d/1iA0QU0CEywwCr-zDswg7C_RwZgLqS3gb/view'
URL_GOOGLE_XLSX_VIEW = 'https://docs.google.com/spreadsheets/d/1iA0QU0CEywwCr-zDswg7C_RwZgLqS3gb/edit#gid=930997768'
URL_GOOGLE_OPEN_SHEET = 'https://drive.google.com/open?id=1VTswL-w9EI0IdGIBFZoZ-2RmIiebXKsrhv03yd7LlIg'
URL_GOOGLE_OPEN_FILE = 'https://drive.google.com/open?id=1iA0QU0CEywwCr-zDswg7C_RwZgLqS3gb'
import pytest


class TestInput(unittest.TestCase):

    @pytest.mark.asyncio
    async def test_array(self):
        self.assertTrue(await make_input(DATA).is_repeatable)
        self.assertTrue('#sector' in await hxl.data(DATA).tags)

    @pytest.mark.asyncio
    async def test_csv_comma_separated(self):
        with await make_input(FILE_CSV, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_csv_hxl_ext(self):
        with await make_input(FILE_CSV_HXL_EXT, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_csv_tab_separated(self):
        with await make_input(FILE_TSV, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_csv_semicolon_separated(self):
        with await make_input(FILE_SSV, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_csv_zipped(self):
        with await make_input(FILE_ZIP_CSV, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_zip_invalid(self):
        """Expect a HXLIOException, not a meaningless TypeError"""
        with self.assertRaises(hxl.input.HXLIOException):
            await make_input(FILE_ZIP_INVALID, InputOptions(allow_local=True))

    @pytest.mark.asyncio
    async def test_binary_invalid(self):
        """ Expect a HXLIOException """
        with self.assertRaises(hxl.input.HXLIOException):
            await make_input(FILE_BINARY_INVALID, InputOptions(allow_local=True))

    @pytest.mark.asyncio
    async def test_csv_latin1(self):
        with await make_input(FILE_CSV_LATIN1, InputOptions(allow_local=True, encoding="latin1")) as input:
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_json_lists(self):
        with await make_input(FILE_JSON, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_json_objects(self):
        with await make_input(FILE_JSON_OBJECTS, InputOptions(allow_local=True)) as input:
            self.assertFalse(input.is_repeatable)
            self.assertTrue('#sector' in await hxl.data(input).tags)

    @pytest.mark.asyncio
    async def test_json_selector(self):
        SEL1_DATA = [["Coast", "100"]]
        SEL2_DATA = [["Plains", "200"]]

        # make sure legacy selectors still work
        with await make_input(FILE_JSON_SELECTOR, InputOptions(allow_local=True, selector="sel1")) as input:
            self.assertEqual(SEL1_DATA, await hxl.data(input).values)
        with await make_input(FILE_JSON_SELECTOR, InputOptions(allow_local=True, selector="sel2")) as input:
            self.assertEqual(SEL2_DATA, await hxl.data(input).values)

        # test JSONPath support
        with await make_input(FILE_JSON_SELECTOR, InputOptions(allow_local=True, selector="$.sel1")) as input:
            self.assertEqual(SEL1_DATA, await hxl.data(input).values)
            
    @pytest.mark.asyncio
    async def test_xls(self):
        with await make_input(FILE_XLS, InputOptions(allow_local=True)) as input:
            self.assertTrue(input.is_repeatable)

    @pytest.mark.asyncio
    async def test_xlsx(self):
        with await make_input(FILE_XLSX, InputOptions(allow_local=True)) as input:
            self.assertTrue(input.is_repeatable)
            header_row = next(iter(input))
            self.assertEqual("¿Qué?", header_row[0])

    @pytest.mark.asyncio
    async def test_xlsx_sheet_index(self):
        # a non-existant sheet should throw an exception
        with self.assertRaises(hxl.input.HXLIOException):
            with await make_input(FILE_XLSX, InputOptions(allow_local=True, sheet_index=100)) as input:
                pass

    @pytest.mark.asyncio
    async def test_xlsx_merged(self):
        with await make_input(FILE_XLSX, InputOptions(allow_local=True, expand_merged=False)) as input:
            self.assertTrue(input.is_repeatable)
            header_row = next(iter(input))
            self.assertEqual("", header_row[1])

        with await make_input(FILE_XLSX, InputOptions(allow_local=True, expand_merged=True)) as input:
            self.assertTrue(input.is_repeatable)
            header_row = next(iter(input))
            self.assertEqual("¿Qué?", header_row[1])

    @pytest.mark.asyncio
    async def test_ckan_resource(self):
        source = await hxl.data('https://data.humdata.org/dataset/hxl-master-vocabulary-list/resource/d22dd1b6-2ff0-47ab-85c6-08aeb911a832')
        self.assertTrue('#vocab' in source.tags)

    @pytest.mark.asyncio
    async def test_ckan_dataset(self):
        source = await hxl.data('https://data.humdata.org/dataset/hxl-master-vocabulary-list')
        self.assertTrue('#vocab' in source.tags)

    @pytest.mark.asyncio
    async def test_bytes_buffer(self):
        """Test reading from a string via BytesIO"""
        source = await hxl.data(io.BytesIO("#org\nOrg A".encode('utf-8')))
        self.assertTrue('#org' in source.tags)

    @pytest.mark.asyncio
    async def test_optional_params(self):
        url = 'https://data.humdata.org/dataset/hxl-master-vocabulary-list/resource/d22dd1b6-2ff0-47ab-85c6-08aeb911a832'
        await hxl.input.make_input(url, InputOptions(verify_ssl=True, timeout=30, http_headers={'User-Agent': 'libhxl-python'}))
        await hxl.data(url, InputOptions(verify_ssl=True, timeout=30, http_headers={'User-Agent': 'libhxl-python'}))

    @pytest.mark.asyncio
    async def test_file_object(self):
        with open(FILE_CSV, 'r') as f:
            self.assertIsNotNone(await hxl.input.make_input(f))
        

class TestUntaggedInput(unittest.TestCase):

    @pytest.mark.asyncio
    async def test_untagged_json(self):
        with await hxl.input.make_input(FILE_JSON_UNTAGGED, InputOptions(allow_local=True)) as input:
            self.assertEqual([
                ['', '¿Qué?', '', '¿Quién?', '¿Para quién?', '', '¿Dónde?', '', '¿Cuándo?'],
                ['Registro', 'Sector/Cluster', 'Subsector', 'Organización', 'Hombres', 'Mujeres', 'País', 'Departamento/Provincia/Estado'],
                ['001', 'WASH', 'Higiene', 'ACNUR', '100', '100', 'Panamá', 'Los Santos', '1 March 2015'],
                ['002', 'Salud', 'Vacunación', 'OMS', '', '', 'Colombia', 'Cauca', ''],
                ['003', 'Educación', 'Formación de enseñadores', 'UNICEF', '250', '300', 'Colombia', 'Chocó', ''],
                ['004', 'WASH', 'Urbano', 'OMS', '80', '95', 'Venezuela', 'Amazonas', '']
            ], list(input))

    @pytest.mark.asyncio
    async def test_untagged_json_objects(self):
        with await hxl.input.make_input(FILE_JSON_OBJECTS_UNTAGGED, InputOptions(allow_local=True)) as input:
            self.assertEqual([
                ['Registro', 'Sector/Cluster', 'Subsector', 'Organización', 'Hombres', 'Mujeres', 'País', 'Departamento/Provincia/Estado'],
                ['001', 'WASH', 'Higiene', 'ACNUR', '100', '100', 'Panamá', 'Los Santos'],
                ['002', 'Salud', 'Vacunación', 'OMS', '', '', 'Colombia', 'Cauca'],
                ['003', 'Educación', 'Formación de enseñadores', 'UNICEF', '250', '300', 'Colombia', 'Chocó'],
                ['004', 'WASH', 'Urbano', 'OMS', '80', '95', 'Venezuela', 'Amazonas']
            ], list(input))

    @pytest.mark.asyncio
    async def test_untagged_zipped_csv(self):
        with await hxl.input.make_input(FILE_ZIP_CSV_UNTAGGED, InputOptions(allow_local=True)) as input:
            self.assertEqual([
                ['Registro', 'Sector/Cluster', 'Subsector', 'Organización', 'Hombres', 'Mujeres', 'País', 'Departamento/Provincia/Estado'],
                ['001', 'WASH', 'Higiene', 'ACNUR', '100', '100', 'Panamá', 'Los Santos'],
                ['002', 'Salud', 'Vacunación', 'OMS', '', '', 'Colombia', 'Cauca'],
                ['003', 'Educación', 'Formación de enseñadores', 'UNICEF', '250', '300', 'Colombia', 'Chocó']
            ], list(input))

    @pytest.mark.asyncio
    async def test_html(self):
        """ Reject HTML for tagging """

        with self.assertRaises(hxl.input.HXLHTMLException):
            input = await hxl.make_input("https://ourairports.com")
            list(input)

        with self.assertRaises(hxl.input.HXLIOException):
            input = await hxl.make_input(FILE_NOTAG1, InputOptions(allow_local=True))
            list(input)

        with self.assertRaises(hxl.input.HXLIOException):
            input = await hxl.make_input(FILE_NOTAG2, InputOptions(allow_local=True))
            list(input)


class TestInfo(unittest.TestCase):
    """ Test hxl.input.info() function on different file types """

    NOHXL_HEADERS = [
        '',
        '¿Qué?',
        '',
        '¿Quién?',
        '¿Para quién?',
        '',
        '¿Dónde?',
        '',
        '¿Cuándo?',
    ]

    HXL_HEADERS = [
        "Registro",
        "Sector/Cluster",
        "Subsector",
        "Organización",
        "Hombres",
        "Mujeres",
        "País",
        "Departamento/Provincia/Estado",
        None,
    ]

    HXL_HASHTAGS = [
        "",
        "#sector+es",
        "#subsector+es",
        "#org+es",
        "#targeted+f",
        "#targeted+m",
        "#country",
        "#adm1",
        "#date+reported",
    ]
    
    @pytest.mark.asyncio
    async def test_xlsx_info(self):
        """ Test the hxl.input.info() function for an XLSX file """

        report = await hxl.input.info(FILE_XLSX_INFO, InputOptions(allow_local=True))
        self.assertEqual("XLSX", report["format"])
        self.assertEqual(2, len(report["sheets"]))

        # Sheet 1: not HXL
        sheet = report["sheets"][0]
        self.assertEqual("input-quality-no-hxl", sheet["name"])
        self.assertFalse(sheet["is_hidden"]),
        self.assertEqual(6, sheet["nrows"]),
        self.assertEqual(9, sheet["ncols"]),
        self.assertTrue(sheet["has_merged_cells"])
        self.assertFalse(sheet["is_hxlated"])
        self.assertEqual("b1c179c6f56b75507e1775ac4b7025d5", sheet["header_hash"])
        self.assertTrue(sheet["hxl_header_hash"] is None)
        self.assertEqual(self.NOHXL_HEADERS, sheet["headers"])
        self.assertIsNone(sheet["hxl_headers"]) # hxl_headers means hashtags

        # Sheet 2: HXL
        sheet = report["sheets"][1]
        self.assertEqual("input-quality-hxl", sheet["name"])
        self.assertFalse(sheet["is_hidden"]),
        self.assertEqual(7, sheet["nrows"]),
        self.assertEqual(9, sheet["ncols"]),
        self.assertFalse(sheet["has_merged_cells"])
        self.assertTrue(sheet["is_hxlated"])
        self.assertEqual("56c6270ee039646436af590e874e6f67", sheet["header_hash"])
        self.assertEqual("ccfd7a84d6697a870e95dd64fbac640c", sheet["hxl_header_hash"])
        self.assertEqual(self.HXL_HEADERS, sheet["headers"])
        self.assertEqual(self.HXL_HASHTAGS, sheet["hxl_headers"])


    @pytest.mark.asyncio
    async def test_xls_info(self):
        report = await hxl.input.info(FILE_XLS_INFO, InputOptions(allow_local=True))
        self.assertEqual("XLS", report["format"])
        self.assertEqual(2, len(report["sheets"]))

        # Sheet 1: no HXL
        sheet = report["sheets"][0]
        self.assertEqual("input-quality-no-hxl", sheet["name"])
        self.assertFalse(sheet["is_hidden"]),
        self.assertEqual(6, sheet["nrows"]),
        self.assertEqual(9, sheet["ncols"]),
        #self.assertTrue(sheet["has_merged_cells"]) # can't detect in XLS yet
        self.assertFalse(sheet["is_hxlated"])
        self.assertEqual("b1c179c6f56b75507e1775ac4b7025d5", sheet["header_hash"])
        self.assertIsNone(sheet["hxl_header_hash"])
        self.assertEqual(self.NOHXL_HEADERS, sheet["headers"])
        self.assertIsNone(sheet["hxl_headers"])

        # Sheet 2: HXL
        sheet = report["sheets"][1]
        self.assertEqual("input-quality-hxl", sheet["name"])
        self.assertFalse(sheet["is_hidden"]),
        self.assertEqual(7, sheet["nrows"]),
        self.assertEqual(9, sheet["ncols"]),
        self.assertFalse(sheet["has_merged_cells"])
        self.assertTrue(sheet["is_hxlated"])
        self.assertEqual("56c6270ee039646436af590e874e6f67", sheet["header_hash"])
        self.assertEqual("ccfd7a84d6697a870e95dd64fbac640c", sheet["hxl_header_hash"])
        self.assertEqual(self.HXL_HEADERS, sheet["headers"])
        self.assertEqual(self.HXL_HASHTAGS, sheet["hxl_headers"])

    @pytest.mark.asyncio
    async def test_csv_info_hxl(self):
        """ Test the hxl.input.info() function for a CSV file """

        report = await hxl.input.info(FILE_CSV, InputOptions(allow_local=True))
        self.assertEqual(FILE_CSV, report["url_or_filename"])
        self.assertEqual("CSV", report["format"])
        self.assertEqual(1, len(report["sheets"]))

        sheet = report["sheets"][0]
        self.assertEqual("__DEFAULT__", sheet["name"])
        self.assertEqual(7, sheet["nrows"])
        self.assertEqual(9, sheet["ncols"])
        self.assertFalse(sheet["is_hidden"])
        self.assertFalse(sheet["has_merged_cells"])
        self.assertTrue(sheet["is_hxlated"])
        self.assertEqual("56c6270ee039646436af590e874e6f67", sheet["header_hash"])
        self.assertEqual("ccfd7a84d6697a870e95dd64fbac640c", sheet["hxl_header_hash"])
        self.assertEqual(self.HXL_HEADERS, sheet["headers"])
        self.assertEqual(self.HXL_HASHTAGS, sheet["hxl_headers"]) # hxl_headers is the hashtag row

    @pytest.mark.asyncio
    async def test_csv_info_nohxl(self):
        """ Test the hxl.input.info() function for a CSV file """

        report = await hxl.input.info(FILE_CSV_UNTAGGED, InputOptions(allow_local=True))
        self.assertEqual(FILE_CSV_UNTAGGED, report["url_or_filename"])
        self.assertEqual("CSV", report["format"])
        self.assertEqual(1, len(report["sheets"]))

        sheet = report["sheets"][0]
        self.assertEqual("__DEFAULT__", sheet["name"])
        self.assertEqual(6, sheet["nrows"])
        self.assertEqual(9, sheet["ncols"])
        self.assertFalse(sheet["is_hidden"])
        self.assertFalse(sheet["has_merged_cells"])
        self.assertFalse(sheet["is_hxlated"])
        self.assertEqual("b1c179c6f56b75507e1775ac4b7025d5", sheet["header_hash"])
        self.assertIsNone(sheet["hxl_header_hash"])
        self.assertEqual(self.NOHXL_HEADERS, sheet["headers"])
        self.assertIsNone(sheet["hxl_headers"]) # hxl_headers is the hashtag row

    @pytest.mark.asyncio
    async def test_json_arrays_info_hxl(self):
        """ Test the hxl.input.info() function for a JSON arrays file """
        
        report = await hxl.input.info(FILE_JSON, InputOptions(allow_local=True))
        self.assertEqual(FILE_JSON, report["url_or_filename"])
        self.assertEqual("JSON", report["format"])
        self.assertEqual(1, len(report["sheets"]))

        sheet = report["sheets"][0]
        self.assertEqual(7, sheet["nrows"])
        self.assertEqual(9, sheet["ncols"])
        self.assertFalse(sheet["is_hidden"])
        self.assertFalse(sheet["has_merged_cells"])
        self.assertTrue(sheet["is_hxlated"])
        self.assertEqual("56c6270ee039646436af590e874e6f67", sheet["header_hash"])
        self.assertEqual("ccfd7a84d6697a870e95dd64fbac640c", sheet["hxl_header_hash"])
        self.assertEqual(self.HXL_HEADERS, sheet["headers"])
        self.assertEqual(self.HXL_HASHTAGS, sheet["hxl_headers"]) # hxl_headers is the hashtag row

    @pytest.mark.asyncio
    async def test_json_arrays_info_nohxl(self):
        """ Test the hxl.input.info() function for a JSON arrays file """
        
        report = await hxl.input.info(FILE_JSON_UNTAGGED, InputOptions(allow_local=True))
        self.assertEqual(FILE_JSON_UNTAGGED, report["url_or_filename"])
        self.assertEqual("JSON", report["format"])
        self.assertEqual(1, len(report["sheets"]))

        sheet = report["sheets"][0]
        self.assertEqual(6, sheet["nrows"])
        self.assertEqual(9, sheet["ncols"])
        self.assertFalse(sheet["is_hidden"])
        self.assertFalse(sheet["has_merged_cells"])
        self.assertFalse(sheet["is_hxlated"])
        self.assertEqual("b1c179c6f56b75507e1775ac4b7025d5", sheet["header_hash"])
        self.assertIsNone(sheet["hxl_header_hash"])
        self.assertEqual(self.NOHXL_HEADERS, sheet["headers"])
        self.assertIsNone(sheet["hxl_headers"]) # hxl_headers is the hashtag row

    @pytest.mark.asyncio
    async def test_json_objects_info(self):
        report = await hxl.input.info(FILE_JSON_OBJECTS, InputOptions(allow_local=True))
        self.assertEqual(1, len(report["sheets"]))
        self.assertEqual("JSON", report["format"])

        sheet = report["sheets"][0]
        self.assertEqual(5, sheet["nrows"])
        self.assertEqual(9, sheet["ncols"])
        self.assertFalse(sheet["is_hidden"])
        self.assertFalse(sheet["has_merged_cells"])
        self.assertTrue(sheet["is_hxlated"])
        self.assertEqual("d41d8cd98f00b204e9800998ecf8427e", sheet["header_hash"])
        self.assertEqual("ccfd7a84d6697a870e95dd64fbac640c", sheet["hxl_header_hash"])

    

class TestFuncs(unittest.TestCase):

    DATA = [
        ['Sector', 'Organisation', 'Province name'],
        ['#sector', '#org', '#adm1'],
        ['WASH', 'Org A', 'Coast'],
        ['Health', 'Org B', 'Plains']
    ]

    ENCODED_URL = "https%3A%2F%2Fexample.org%2Fdata.csv"

    INPUT_OPTIONS = hxl.input.InputOptions()

    # TODO - add tests for munging other types of URLs

    @pytest.mark.asyncio
    async def test_url_munging_hxl_proxy(self):

        # add .csv to data
        url_in = "https://proxy.hxlstandard.org/data?url=$ENCODED_URL"
        url_out = "https://proxy.hxlstandard.org/data.csv?url=$ENCODED_URL"
        self.assertEqual(url_out, await hxl.input.munge_url(url_in, self.INPUT_OPTIONS))

        # strip /edit
        url_in = "https://proxy.hxlstandard.org/data/edit?url=$ENCODED_URL"
        url_out = "https://proxy.hxlstandard.org/data.csv?url=$ENCODED_URL"
        self.assertEqual(url_out, await hxl.input.munge_url(url_in, self.INPUT_OPTIONS))

        # data/download should be unaltered
        url_in = "https://proxy.hxlstandard.org/data/download/foo.csv"
        url_out = "https://proxy.hxlstandard.org/data/download/foo.csv"
        self.assertEqual(url_out, await hxl.input.munge_url(url_in, self.INPUT_OPTIONS))

    @pytest.mark.asyncio
    async def test_from_spec_tagged(self):
        source = await hxl.from_spec({
            'input': self.DATA,
            'recipe': [
                {
                    'filter': 'cache'
                }
            ]
        })
        self.assertEqual(self.DATA[2:], source.values)

    @pytest.mark.asyncio
    async def test_from_spec_untagged(self):
        source = await hxl.from_spec({
            'input': self.DATA[0:1]+self.DATA[2:],
            'tagger': {
                'specs': {
                    'sector': '#sector',
                    'organisation': '#org',
                    'province name': '#adm1'
                }
            },
            'recipe': [
                {
                    'filter': 'cache'
                }
            ]
        })
        self.assertEqual(self.DATA[2:], source.values)


class TestBadInput(unittest.TestCase):

    @pytest.mark.asyncio
    async def test_bad_file(self):
        with self.assertRaises(IOError):
            source = await hxl.data('XXXXX', InputOptions(allow_local=True))

    @pytest.mark.asyncio
    async def test_bad_url(self):
        with self.assertRaises(IOError):
            source = await hxl.data('http://x.localhost/XXXXX', InputOptions(timeout=1))

    @pytest.mark.asyncio
    async def test_local_file_fails(self):
        with self.assertRaises(hxl.input.HXLIOException):
            # allow_local should default to False
            source = await hxl.data("/etc/passwd")

    @pytest.mark.asyncio
    async def test_ip_address_fails(self):
        with self.assertRaises(hxl.input.HXLIOException):
            # allow_local should default to False
            source = await hxl.data("http://127.0.0.1/index.html")

    @pytest.mark.asyncio
    async def test_localhost_fails(self):
        with self.assertRaises(hxl.input.HXLIOException):
            # allow_local should default to False
            source = await hxl.data("http://localhost/index.html")

    @pytest.mark.asyncio
    async def test_localdomain_fails(self):
        with self.assertRaises(hxl.input.HXLIOException):
            # allow_local should default to False
            source = await hxl.data("http://foo.localdomain/index.html")
            

class TestParser(unittest.TestCase):

    EXPECTED_ROW_COUNT = 4
    EXPECTED_HEADERS = ['Registro', 'Sector/Cluster','Subsector','Organización','Hombres','Mujeres','País','Departamento/Provincia/Estado', None]
    EXPECTED_TAGS = [None, '#sector', '#subsector', '#org', '#targeted', '#targeted', '#country', '#adm1', '#date']
    EXPECTED_ATTRIBUTES = [{}, {'es'}, {'es'}, {'es'}, {'f'}, {'m'}, {}, {}, {'reported'}]
    EXPECTED_CONTENT = [
        ['001', 'WASH', 'Higiene', 'ACNUR', '100', '100', 'Panamá', 'Los Santos', '1 March 2015'],
        ['002', 'Salud', 'Vacunación', 'OMS', '', '', 'Colombia', 'Cauca', ''],
        ['003', 'Educación', 'Formación de enseñadores', 'UNICEF', '250', '300', 'Colombia', 'Chocó', ''],
        ['004', 'WASH', 'Urbano', 'OMS', '80', '95', 'Venezuela', 'Amazonas', '']
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @pytest.mark.asyncio
    async def test_row_count(self):
        row_count = 0
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            # logical row count
            for row in source:
                row_count += 1
        self.assertEqual(TestParser.EXPECTED_ROW_COUNT, row_count)

    @pytest.mark.asyncio
    async def test_headers(self):
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            headers = source.headers
        self.assertEqual(TestParser.EXPECTED_HEADERS, headers)

    @pytest.mark.asyncio
    async def test_tags(self):
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            tags = source.tags
        self.assertEqual(TestParser.EXPECTED_TAGS, tags)

    @pytest.mark.asyncio
    async def test_empty_header_row(self):
        """Test for exception parsing an empty header row"""
        DATA = [
            [],
            ['X', 'Y'],
            ['#adm1', '#affected'],
            ['Coast', '100']
        ]
        await hxl.data(DATA).columns

    @pytest.mark.asyncio
    async def test_attributes(self):
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            for row in source:
                for column_number, column in enumerate(row.columns):
                    self.assertEqual(set(TestParser.EXPECTED_ATTRIBUTES[column_number]), column.attributes)

    @pytest.mark.asyncio
    async def test_column_count(self):
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            for row in source:
                self.assertEqual(len(TestParser.EXPECTED_TAGS), len(row.values))

    @pytest.mark.asyncio
    async def test_columns(self):
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            for row in source:
                for column_number, column in enumerate(row.columns):
                    self.assertEqual(TestParser.EXPECTED_TAGS[column_number], column.tag)

    @pytest.mark.asyncio
    async def test_multiline(self):
        with await hxl.data(FILE_MULTILINE, InputOptions(allow_local=True)) as source:
            for row in source:
                self.assertEqual("Line 1\nLine 2\nLine 3", row.get('description'))

    @pytest.mark.asyncio
    async def test_local_csv(self):
        """Test reading from a local CSV file."""
        with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_xlsx(self):
        """Test reading from a local XLSX file."""
        with await hxl.data(FILE_XLSX, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_xls(self):
        """Test reading from a local XLS (legacy) file."""
        with await hxl.data(FILE_XLS, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_xlsx_broken(self):
        """Test reading from a local XLSX file."""
        with await hxl.data(FILE_XLSX_BROKEN, InputOptions(allow_local=True)) as source:
            source.columns # just do something 

    @pytest.mark.asyncio
    async def test_local_xlsx_wrong_ext(self):
        """Test reading from a local XLSX file with the wrong extension."""
        with await hxl.data(FILE_XLSX_NOEXT, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_json(self):
        """Test reading from a local JSON file."""
        with await hxl.data(FILE_JSON, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_json_text(self):
        """Test reading from a local JSON file that doesn't have a JSON extension."""
        with await hxl.data(FILE_JSON_TXT, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_json_objects(self):
        """Test reading from a local JSON file."""
        with await hxl.data(FILE_JSON_OBJECTS, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_local_json_nested(self):
        """Test reading from a local JSON file."""
        with await hxl.data(FILE_JSON_NESTED, InputOptions(allow_local=True)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_remote_csv(self):
        """Test reading from a remote CSV file (will fail without connectivity)."""
        with await hxl.data(URL_CSV, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_remote_csv_hxl_ext(self):
        """Test reading from a remote CSV file with a .hxl extension (will fail without connectivity)."""
        with await hxl.data(URL_CSV_HXL_EXT, InputOptions(timeout=10)) as source:
            self.assertTrue('#country' in source.tags)

    @pytest.mark.asyncio
    async def test_remote_xlsx(self):
        """Test reading from a remote XLSX file (will fail without connectivity)."""
        with await hxl.data(URL_XLSX, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_remote_xls(self):
        """Test reading from a remote XLSX file (will fail without connectivity)."""
        with await hxl.data(URL_XLS, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    def x_test_remote_json(self):
        """Test reading from a remote JSON file (will fail without connectivity)."""
        with hxl.data(URL_JSON) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_sheet_nohash(self):
        # Google Sheet, default tab
        with await hxl.data(URL_GOOGLE_SHEET_NOHASH, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_sheet_hash(self):
        # Google Sheet, specific tab
        with await hxl.data(URL_GOOGLE_SHEET_HASH, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_file(self):
        # Google Sheet, specific tab
        with await hxl.data(URL_GOOGLE_FILE, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_drive_sheet(self):
        # Google Drive, "open" link for sheet
        with await hxl.data(URL_GOOGLE_OPEN_SHEET, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_drive_file(self):
        # Google Drive, "open" link for file
        with await hxl.data(URL_GOOGLE_OPEN_FILE, InputOptions(timeout=20)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_google_xlsx_view(self):
        # Google drive XLSX in view mode
        with await hxl.data(URL_GOOGLE_XLSX_VIEW, InputOptions(timeout=10)) as source:
            self.compare_input(source)

    @pytest.mark.asyncio
    async def test_fuzzy(self):
        """Imperfect hashtag row should still work."""
        with await hxl.data(FILE_FUZZY, InputOptions(allow_local=True)) as source:
            source.tags

    @pytest.mark.asyncio
    async def test_invalid(self):
        """Missing hashtag row should raise an exception."""
        with self.assertRaises(HXLParseException):
            with await hxl.data(FILE_INVALID, InputOptions(allow_local=True)) as source:
                source.tags

    def compare_input(self, source):
        """Compare an external source to the expected content."""
        for i, row in enumerate(source):
            for j, value in enumerate(row):
                if value is None:
                    value = ''
                # For XLSX, numbers may be pre-parsed
                try:
                    self.assertEqual(float(TestParser.EXPECTED_CONTENT[i][j]), float(value))
                except:
                    self.assertEqual(TestParser.EXPECTED_CONTENT[i][j], value)


class TestLocationInformation(unittest.TestCase):
    """Test location information for rows and columns"""

    @pytest.mark.asyncio
    async def test_multiple_header_row_number(self):
        with await hxl.data(_resolve_file('files/test_io/input-multiple-headers.csv'), InputOptions(allow_local=True)) as source:
            for row in source:
                self.assertEqual(row.source_row_number, row.row_number+3) # there are two header rows and the hashtags
                for i, column in enumerate(row.columns):
                    self.assertEqual(i, column.column_number)

    @pytest.mark.asyncio
    async def test_google_row_number(self):
        source = await hxl.data('https://docs.google.com/spreadsheets/d/1rOO0-xYa3kIOfI-6KR-mLgMTdgIEijNxM52Nfhs8uvg/edit#gid=0')
        for row in source:
            self.assertTrue(row.source_row_number is not None)
            self.assertEqual(row.source_row_number, row.row_number+1) # there are two header rows and the hashtags
            for i, column in enumerate(row.columns):
                self.assertEqual(i, column.column_number)

class TestFunctions(unittest.TestCase):
    """Test module-level convenience functions."""

    DATA_TAGGED = [
        ["District", "Sector", "Organisation"],
        ["#adm1", "#sector", "#org"],
        ["Coast", "Health", "NGO A"],
        ["Plains", "Education", "NGO B"],
        ["Forest", "WASH", "NGO C"],
    ]

    DATA_UNTAGGED = [
        ["District", "Sector", "Organisation"],
        ["Coast", "Health", "NGO A"],
        ["Plains", "Education", "NGO B"],
        ["Forest", "WASH", "NGO C"],
    ]

    @pytest.mark.asyncio
    async def test_tagger(self):
        input = await hxl.input.tagger(TestFunctions.DATA_UNTAGGED, {
                "District": "#org"
        })
        self.assertEqual(TestFunctions.DATA_UNTAGGED[1:], [row.values for row in input])

    @pytest.mark.asyncio
    async def test_write_csv(self):
        with open(FILE_CSV_OUT, 'rb') as input:
            expected = input.read()
            buffer = StringIO()
            with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
                hxl.input.write_hxl(buffer, source)
                # Need to work with bytes to handle CRLF
                self.assertEqual(expected, buffer.getvalue().encode('utf-8'))

    @pytest.mark.asyncio
    async def test_write_json_lists(self):
        with open(FILE_JSON_OUT) as input:
            expected = input.read()
            buffer = StringIO()
            with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
                hxl.input.write_json(buffer, source)
                self.assertEqual(expected, buffer.getvalue())

    @pytest.mark.asyncio
    async def test_write_json_objects(self):
        with open(FILE_JSON_OBJECTS_OUT) as input:
            expected = input.read()
            buffer = StringIO()
            with await hxl.data(FILE_CSV, InputOptions(allow_local=True)) as source:
                hxl.input.write_json(buffer, source, use_objects=True)
                self.assertEqual(expected, buffer.getvalue())

    @pytest.mark.asyncio
    async def test_write_json_attribute_normalisation(self):
        DATA_IN = [
            ['#sector+es+cluster'],
            ['Hygiene']
        ]
        DATA_OUT = [
            {
                '#sector+cluster+es': 'Hygiene'
            }
        ]
        buffer = StringIO()
        source = await hxl.data(DATA_IN)
        hxl.input.write_json(buffer, source, use_objects=True)
        self.assertEqual(DATA_OUT, json.loads(buffer.getvalue()))
            
