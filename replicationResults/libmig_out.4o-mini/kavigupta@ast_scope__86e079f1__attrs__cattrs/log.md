## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/kavigupta@ast_scope__86e079f1__attrs__cattrs/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating ast_scope/scope.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/argument_test.py::DefaultArguments::test_complex_expression_default: passed != not found`
- `tests/argument_test.py::DefaultArguments::test_default_arguments: passed != not found`
- `tests/argument_test.py::DefaultArguments::test_inherits_proper_parent: passed != not found`
- `tests/argument_test.py::DefaultArguments::test_type: passed != not found`
- `tests/argument_test.py::DefaultArguments::test_typing: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_keyword_arguments: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_keyword_only_arguments: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_multiple_arguments: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_positional_only_arguments: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_star_args: passed != not found`
- `tests/argument_test.py::DifferentArgumentTypes::test_starstar_kwargs: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_aug_assignment: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_basic_assignment: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_element_assignment: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_multi_assignment: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_special_assigment: passed != not found`
- `tests/assignment_test.py::EqualityAssignmentTests::test_underscore: passed != not found`
- `tests/assignment_test.py::ImportAssignmentTests::test_aliases: passed != not found`
- `tests/assignment_test.py::ImportAssignmentTests::test_global_import: passed != not found`
- `tests/assignment_test.py::ImportAssignmentTests::test_local_import: passed != not found`
- `tests/assignment_test.py::ImportAssignmentTests::test_star_import: passed != not found`
- `tests/assignment_test.py::ImportAssignmentTests::test_sub_import: passed != not found`
- `tests/assignment_test.py::LoopAssignmentTests::test_basic_for_loop: passed != not found`
- `tests/assignment_test.py::LoopAssignmentTests::test_itemizer_loop: passed != not found`
- `tests/assignment_test.py::LoopAssignmentTests::test_multi_for_loop: passed != not found`
- `tests/basic_scope_test.py::GlobalFrameTest::test_function: passed != not found`
- `tests/basic_scope_test.py::GlobalFrameTest::test_global_augassign: passed != not found`
- `tests/basic_scope_test.py::GlobalFrameTest::test_global_var: passed != not found`
- `tests/basic_scope_test.py::GlobalFrameTest::test_lookups: passed != not found`
- `tests/basic_scope_test.py::GlobalFrameTest::test_multiline_global: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_complex_target: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_dict_comprehension: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_gen_comprehension: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_inherits_parent: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_listcomp: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_listcomp_with_if: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_multi_if: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_nested_listcomp: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_serial_listcomp: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_serial_listcomp_with_if: passed != not found`
- `tests/comprehension_test.py::FunctionFrameTest::test_set_comprehension: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testEmptyGraph: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testFunctionWithNoGlobals: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testGraphDirection: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testJustVariables: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testLocalFunctionsDontGetNodes: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testRecursiveFunction: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testReferenceToImport: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testRefersToImportStatements: passed != not found`
- `tests/dependency_graph_test.py::TestClassDefault::testRefersToVariables: passed != not found`
- `tests/exception_test.py::ExceptionTests::test_multiple_arguments: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_async_parameters_new: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_async_parameters_old: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_decorator_top_level_new: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_decorator_top_level_old: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_def_is_assign: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_global_statement: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_inherits: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_nested_function: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_no_parameter_function: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_not_found_to_be_global: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_parameters: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_self_reference: passed != not found`
- `tests/function_frame_test.py::FunctionFrameTest::test_set_after_get: passed != not found`
- `tests/lambda_test.py::FunctionFrameTest::test_basic_lambda: passed != not found`
- `tests/lambda_test.py::FunctionFrameTest::test_default_params_in_parent: passed != not found`
- `tests/lambda_test.py::FunctionFrameTest::test_multiarg_lambda: passed != not found`
- `tests/lambda_test.py::FunctionFrameTest::test_nested_lambdas: passed != not found`
- `tests/lambda_test.py::FunctionFrameTest::test_noarg_lambda: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_basic_nonlocal: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_global_escapes_scope: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_global_escapes_scope_even_without_declaration: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_no_nonlocal: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_nonlocal_found_in_most_recent_parent: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_nonlocal_found_in_parent_of_parent: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_nonlocal_not_found: passed != not found`
- `tests/nonlocal_test.py::NonlocalTest::test_symbol_in_different_frame_from_parent: passed != not found`
- `tests/special_symbols_test.py::SpecialSymbolsTest::test_booleans: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
