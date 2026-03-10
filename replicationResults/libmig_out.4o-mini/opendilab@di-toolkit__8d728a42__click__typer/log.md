## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/opendilab@di-toolkit__8d728a42__click__typer/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating ditk/doc/annotated/__main__.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/config/test_meta.py::TestConfigMeta::test_title: passed != not found`
- `test/doc/annotated/test_generate.py::test_generate: passed != not found`
- `test/logging/test_func.py::TestLoggingFunc::test_loggings: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[BASIC_FORMAT]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[BufferingFormatter]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[CRITICAL]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[DEBUG]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[ERROR]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[FATAL]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[FileHandler]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[Filter]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[Formatter]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[Handler]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[INFO]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[LogRecord]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[LoggerAdapter]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[Logger]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[NOTSET]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[NullHandler]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[StreamHandler]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[WARNING]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[WARN]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[addLevelName]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[basicConfig]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[captureWarnings]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[disable]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[getLevelName]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[getLevelNamesMapping]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[getLogRecordFactory]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[getLoggerClass]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[lastResort]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[makeLogRecord]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[raiseExceptions]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[setLogRecordFactory]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[setLoggerClass]: passed != not found`
- `test/logging/test_inherit.py::TestLoggingInherit::test_inherit[shutdown]: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_new_files: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_new_level: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_simple_rich: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_simple_rich_with_style: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_simple_rich_with_style_disable_rich: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_stream: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_with_basic_rich: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_with_basic_stream: passed != not found`
- `test/logging/test_log.py::TestLoggingLog::test_with_files: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_extract_log_tb1_sac: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_extract_recursive_logs_tb1: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_extract_recursive_logs_tb1_sac: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_has_log[segs0-False]: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_has_log[segs1-True]: passed != not found`
- `test/tensorboard/test_log.py::TestTensorboardLog::test_tb_has_log[segs2-True]: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
