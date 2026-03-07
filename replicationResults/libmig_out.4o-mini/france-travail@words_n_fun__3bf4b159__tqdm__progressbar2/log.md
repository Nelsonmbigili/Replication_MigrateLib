## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/france-travail@words_n_fun__3bf4b159__tqdm__progressbar2/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating words_n_fun/__init__.py
### migrating words_n_fun/preprocessing/basic.py
### migrating words_n_fun/preprocessing/split_sentences.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_2_basic.py::BasicTests::test_lemmatize: passed != failed`
- `tests/test_2_basic.py::BasicTests::test_remove_gender_synonyms: passed != failed`
- `tests/test_2_basic.py::BasicTests::test_remove_stopwords: passed != failed`
- `tests/test_3_api.py::ApiTests::test_PreProcessor: passed != failed`
- `tests/test_3_api.py::ApiTests::test_preprocess_pipeline: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
