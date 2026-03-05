## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/kura@yarg__6378a9f4__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating yarg/client.py
### migrating yarg/exceptions.py
### migrating yarg/parse.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_client.py::TestClient::test_end_slash: passed != not found`
- `tests/test_client.py::TestClient::test_get: passed != not found`
- `tests/test_exceptions.py::TestHTTPErrorNoReason::test_repr: passed != not found`
- `tests/test_exceptions.py::TestHTTPErrorNoReason::test_str: passed != not found`
- `tests/test_exceptions.py::TestHTTPErrorWithReason::test_repr: passed != not found`
- `tests/test_exceptions.py::TestHTTPErrorWithReason::test_str: passed != not found`
- `tests/test_package.py::TestPackage::test_author: passed != not found`
- `tests/test_package.py::TestPackage::test_bugtracker: passed != not found`
- `tests/test_package.py::TestPackage::test_classifiers: passed != not found`
- `tests/test_package.py::TestPackage::test_description: passed != not found`
- `tests/test_package.py::TestPackage::test_docs: passed != not found`
- `tests/test_package.py::TestPackage::test_downloads: passed != not found`
- `tests/test_package.py::TestPackage::test_has_egg: passed != not found`
- `tests/test_package.py::TestPackage::test_has_source: passed != not found`
- `tests/test_package.py::TestPackage::test_has_wheel: passed != not found`
- `tests/test_package.py::TestPackage::test_homepage: passed != not found`
- `tests/test_package.py::TestPackage::test_latest_release_id: passed != not found`
- `tests/test_package.py::TestPackage::test_license: passed != not found`
- `tests/test_package.py::TestPackage::test_license_from_classifiers: passed != not found`
- `tests/test_package.py::TestPackage::test_maintainer: passed != not found`
- `tests/test_package.py::TestPackage::test_name: passed != not found`
- `tests/test_package.py::TestPackage::test_pypi_url: passed != not found`
- `tests/test_package.py::TestPackage::test_python_implementations: passed != not found`
- `tests/test_package.py::TestPackage::test_python_versions: passed != not found`
- `tests/test_package.py::TestPackage::test_release_ids: passed != not found`
- `tests/test_package.py::TestPackage::test_repr: passed != not found`
- `tests/test_package.py::TestPackage::test_summary: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_bugtracker: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_docs: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_has_egg: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_has_source: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_has_wheel: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_homepage: passed != not found`
- `tests/test_package.py::TestPackageMissingData::test_latest_release_id: passed != not found`
- `tests/test_parse.py::TestParse::test_newest_package: passed != not found`
- `tests/test_parse.py::TestParse::test_newest_package_repr: passed != not found`
- `tests/test_parse.py::TestParse::test_newest_package_version: passed != not found`
- `tests/test_parse.py::TestParse::test_newest_packages: passed != not found`
- `tests/test_parse.py::TestParse::test_newest_packages_bad_get: passed != not found`
- `tests/test_parse.py::TestParse::test_updated_package: passed != not found`
- `tests/test_parse.py::TestParse::test_updated_package_repr: passed != not found`
- `tests/test_parse.py::TestParse::test_updated_packages: passed != not found`
- `tests/test_parse.py::TestParse::test_updated_packages_bad_get: passed != not found`
- `tests/test_release.py::TestRelease::test_latest_release: passed != not found`
- `tests/test_release.py::TestRelease::test_latest_release_id: passed != not found`
- `tests/test_release.py::TestRelease::test_release: passed != not found`
- `tests/test_release.py::TestRelease::test_release_filename: passed != not found`
- `tests/test_release.py::TestRelease::test_release_has_sig: passed != not found`
- `tests/test_release.py::TestRelease::test_release_id: passed != not found`
- `tests/test_release.py::TestRelease::test_release_ids: passed != not found`
- `tests/test_release.py::TestRelease::test_release_md5: passed != not found`
- `tests/test_release.py::TestRelease::test_release_package_type: passed != not found`
- `tests/test_release.py::TestRelease::test_release_python_version: passed != not found`
- `tests/test_release.py::TestRelease::test_release_size: passed != not found`
- `tests/test_release.py::TestRelease::test_release_unknown_package_type: passed != not found`
- `tests/test_release.py::TestRelease::test_release_uploaded: passed != not found`
- `tests/test_release.py::TestRelease::test_release_url: passed != not found`
- `tests/test_release.py::TestRelease::test_repr: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
