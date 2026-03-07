## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/danajomar@pyale__d6afae67__matplotlib__plotly/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 4 files
### migrating PyALE/_src/ALE_1D.py
### migrating PyALE/_src/ALE_2D.py
### migrating tests/test_1D_ale.py
### migrating tests/test_2D_ale.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_1D_ale.py::Test1DContinuous::test_CIvalues: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_bins: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_binsizes: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_effvalues: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_exceptions: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_indexname: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_outputshape_noCI: passed != failed`
- `tests/test_1D_ale.py::Test1DContinuous::test_outputshape_withCI: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_CIvalues: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_bins: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_binsizes: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_effvalues: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_exceptions: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_indexname: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_outputshape_noCI: passed != failed`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_outputshape_withCI: passed != failed`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_ci_plot: passed != failed`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_line_plot: passed != failed`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_rug_plot: passed != failed`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_bar_plot: passed != failed`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_ci_plot: passed != failed`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_line_plot: passed != failed`
- `tests/test_ale.py::Testale::test_1D_continuous_plot_called: passed != failed`
- `tests/test_ale.py::Testale::test_1D_discrete_plot_called: passed != failed`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_1D_ale.py::Test1DContinuous::test_CIvalues: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_bins: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_binsizes: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_effvalues: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_exceptions: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_indexname: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_outputshape_noCI: passed != not found`
- `tests/test_1D_ale.py::Test1DContinuous::test_outputshape_withCI: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_CIvalues: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_bins: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_binsizes: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_effvalues: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_exceptions: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_indexname: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_outputshape_noCI: passed != not found`
- `tests/test_1D_ale.py::Test1Ddiscrete::test_outputshape_withCI: passed != not found`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_ci_plot: passed != not found`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_line_plot: passed != not found`
- `tests/test_1D_ale.py::TestContPlottingFun::test_1D_continuous_rug_plot: passed != not found`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_bar_plot: passed != not found`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_ci_plot: passed != not found`
- `tests/test_1D_ale.py::TestDiscPlottingFun::test_1D_continuous_line_plot: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_2D_continuous_grid_plot: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_bins: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_effvalues: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_effvalues_g50: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_indexnames: passed != not found`
- `tests/test_2D_ale.py::Test2DFunctions::test_outputshape: passed != not found`
- `tests/test_ale.py::Testale::test_1D_continuous_plot_called: passed != not found`
- `tests/test_ale.py::Testale::test_1D_discrete_plot_called: passed != not found`
- `tests/test_ale.py::Testale::test_2D_continuous_called: passed != not found`
- `tests/test_ale.py::Testale::test_2D_continuous_plot_called: passed != not found`
- `tests/test_ale.py::Testale::test_auto_calls_1D_continuous: passed != not found`
- `tests/test_ale.py::Testale::test_auto_calls_1D_discrete: passed != not found`
- `tests/test_ale.py::Testale::test_contin_calls_1D_continuous: passed != not found`
- `tests/test_ale.py::Testale::test_discr_calls_1D_discrete: passed != not found`
- `tests/test_ale.py::Testale::test_exceptions: passed != not found`
- `tests/test_lib.py::TestlibFunctions::test_cmds: passed != not found`
- `tests/test_lib.py::TestlibFunctions::test_order_groups: passed != not found`
- `tests/test_lib.py::TestlibFunctions::test_quantile_ied: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
