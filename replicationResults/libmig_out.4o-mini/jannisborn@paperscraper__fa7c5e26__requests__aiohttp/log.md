## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/jannisborn@paperscraper__fa7c5e26__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 4 files
### migrating paperscraper/get_dumps/utils/chemrxiv/chemrxiv_api.py
### migrating paperscraper/get_dumps/utils/chemrxiv/utils.py
### migrating paperscraper/pdf.py
### migrating paperscraper/xrxiv/xrxiv_api.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `paperscraper/citations/tests/test_self_references.py::TestSelfReferences::test_compare_async_and_sync_performance: passed != not found`
- `paperscraper/citations/tests/test_self_references.py::TestSelfReferences::test_multiple_dois: passed != not found`
- `paperscraper/pubmed/tests/test_pubmed.py::TestPubMed::test_email: passed != not found`
- `paperscraper/pubmed/tests/test_pubmed.py::TestPubMed::test_get_and_dump_pubmed: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_arxiv_dumping: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_biorxiv: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_biorxiv_date: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dump_existence: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dump_existence_initial: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dumping: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_medrxiv: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_basic_search: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_fuzzy_search: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_impact_factor_filtering: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_nlm_id: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_return_all_fields: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_sort_by_score: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_type_error: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_value_error: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_incorrect_filepath_extension: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_incorrect_filepath_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_invalid_filepath_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_invalid_metadata_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_doi: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_doi_key: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_pdf_url_in_meta_tags: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_network_issues_on_doi_url_request: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_network_issues_on_pdf_url_request: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_nonexistent_directory_in_filepath: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_without_path: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_key: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_key_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_output_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_suffix: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_type: passed != not found`
- `paperscraper/xrxiv/tests/test_xrxiv.py::TestXRXiv::test_get_medrxiv: passed != not found`
- `paperscraper/xrxiv/tests/test_xrxiv.py::TestXRXiv::test_xriv_querier: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 9 functions to mark async including 0 tests
- Found 6 calls to await
- 5 files requires transformation
- transforming paperscraper/get_dumps/utils/chemrxiv/utils.py
- transforming paperscraper/get_dumps/chemrxiv.py
- transforming paperscraper/xrxiv/xrxiv_api.py
- transforming paperscraper/tests/test_dump.py
- transforming paperscraper/get_dumps/utils/chemrxiv/chemrxiv_api.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `paperscraper/citations/tests/test_self_references.py::TestSelfReferences::test_compare_async_and_sync_performance: passed != not found`
- `paperscraper/citations/tests/test_self_references.py::TestSelfReferences::test_multiple_dois: passed != not found`
- `paperscraper/pubmed/tests/test_pubmed.py::TestPubMed::test_email: passed != not found`
- `paperscraper/pubmed/tests/test_pubmed.py::TestPubMed::test_get_and_dump_pubmed: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_arxiv_dumping: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_biorxiv: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_biorxiv_date: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dump_existence: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dump_existence_initial: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_dumping: passed != not found`
- `paperscraper/tests/test_dump.py::TestDumper::test_medrxiv: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_basic_search: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_fuzzy_search: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_impact_factor_filtering: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_nlm_id: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_return_all_fields: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_sort_by_score: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_type_error: passed != not found`
- `paperscraper/tests/test_impactor.py::TestImpactor::test_value_error: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_incorrect_filepath_extension: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_incorrect_filepath_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_invalid_filepath_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_invalid_metadata_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_doi: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_doi_key: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_missing_pdf_url_in_meta_tags: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_network_issues_on_doi_url_request: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_network_issues_on_pdf_url_request: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_nonexistent_directory_in_filepath: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_without_path: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_key: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_key_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_output_type: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_suffix: passed != not found`
- `paperscraper/tests/test_pdf.py::TestPDF::test_save_pdf_from_dump_wrong_type: passed != not found`
- `paperscraper/xrxiv/tests/test_xrxiv.py::TestXRXiv::test_get_medrxiv: passed != not found`
- `paperscraper/xrxiv/tests/test_xrxiv.py::TestXRXiv::test_xriv_querier: passed != not found`
- async_transform finished
