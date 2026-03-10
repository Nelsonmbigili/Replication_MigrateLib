## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/blingenf@copydetect__ba072818__pygments__rich/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating copydetect/utils.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_detector.py::TestParameters::test_disable_filtering: passed != not found`
- `tests/test_detector.py::TestParameters::test_encoding_specification: passed != not found`
- `tests/test_detector.py::TestParameters::test_force_language: passed != not found`
- `tests/test_detector.py::TestParameters::test_ignore_leaf: passed != not found`
- `tests/test_detector.py::TestParameters::test_out_file: passed != not found`
- `tests/test_detector.py::TestParameters::test_same_name_only: passed != not found`
- `tests/test_detector.py::TestParameters::test_truncation: passed != not found`
- `tests/test_detector.py::TestTwoFileAPIDetection::test_compare: passed != not found`
- `tests/test_detector.py::TestTwoFileAPIDetection::test_compare_boilerplate: passed != not found`
- `tests/test_detector.py::TestTwoFileDetection::test_compare: passed != not found`
- `tests/test_detector.py::TestTwoFileDetection::test_compare_boilerplate: passed != not found`
- `tests/test_detector.py::TestTwoFileDetection::test_compare_manual_config: passed != not found`
- `tests/test_detector.py::TestTwoFileDetection::test_compare_saving: passed != not found`
- `tests/test_detector.py::TestTwoFileDetection::test_severalfiles: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowDensity::test_winnow_density: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowOutput::test_winnow_1: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowOutput::test_winnow_2: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowOutput::test_winnow_3: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowOutput::test_winnow_empty: passed != not found`
- `tests/test_pywinnowing.py::TestWinnowOutput::test_winnow_inf: passed != not found`
- `tests/test_sanity_checks.py::test_rot_c: passed != not found`
- `tests/test_sanity_checks.py::test_sample_xml: passed != not found`
- `tests/test_utils.py::TestSmallDoc::test_doc_overlap: passed != not found`
- `tests/test_utils.py::TestSmallDoc::test_doc_overlap_boilerplate: passed != not found`
- `tests/test_utils.py::TestSmallDoc::test_highlighting: passed != not found`
- `tests/test_utils.py::TestSmallDoc::test_slice_computation: passed != not found`
- `tests/test_utils.py::TestTokenizerOtherSamples::test_c_tokenization: passed != not found`
- `tests/test_utils.py::TestTokenizerOtherSamples::test_get_token_coverage: passed != not found`
- `tests/test_utils.py::TestTokenizerOtherSamples::test_java_tokenization: passed != not found`
- `tests/test_utils.py::TestTokenizerOtherSamples::test_php_tokenization: passed != not found`
- `tests/test_utils.py::TestTokenizerPythonSample::test_copydetect: passed != not found`
- `tests/test_utils.py::TestTokenizerPythonSample::test_tokenization: passed != not found`
- `tests/test_winnowing.py::TestWinnowDensity::test_winnow_density: passed != not found`
- `tests/test_winnowing.py::TestWinnowOutput::test_winnow_1: passed != not found`
- `tests/test_winnowing.py::TestWinnowOutput::test_winnow_2: passed != not found`
- `tests/test_winnowing.py::TestWinnowOutput::test_winnow_3: passed != not found`
- `tests/test_winnowing.py::TestWinnowOutput::test_winnow_empty: passed != not found`
- `tests/test_winnowing.py::TestWinnowOutput::test_winnow_inf: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
