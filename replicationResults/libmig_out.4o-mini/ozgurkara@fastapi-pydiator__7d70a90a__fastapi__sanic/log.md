## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/ozgurkara@fastapi-pydiator__7d70a90a__fastapi__sanic/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 4 files
### migrating app/application.py
### migrating app/resources/health_check/health_check_resource.py
### migrating app/resources/todo/todo_resource.py
### migrating app/utils/exception/exception_handlers.py
### running tests
- test finished with status 4, cov finished with status 1
### test diff with round premig
- `tests/integration/resources/healt_check/test_health_check_resource.py::TestTodo::test_get: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_add_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_add_todo_should_return_unprocessable_when_invalid_entity: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_delete_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_get_todo_all: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_get_todo_by_id: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_update_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_update_todo_should_return_unprocessable_when_invalid_entity: passed != not found`
- `tests/unit/data/todo/usecases/test_add_todo_data.py::TestAddTodoDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/data/todo/usecases/test_delete_todo_by_id_data.py::TestDeleteTodoByIdDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/data/todo/usecases/test_delete_todo_by_id_data.py::TestDeleteTodoByIdDataUseCase::test_handle_return_success_false_when_todo_is_not_exist: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_handle_return_empty_list: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_handle_return_list: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_request_cache_parameter: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdDataUseCase::test_handle_return_none_when_todo_is_not_exist: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdDataUseCase::test_handle_return_todo: passed != not found`
- `tests/unit/data/todo/usecases/test_update_todo_data.py::TestUpdateTodoDataUseCase::test_handle_return_exception_when_todo_not_found: passed != not found`
- `tests/unit/data/todo/usecases/test_update_todo_data.py::TestUpdateTodoDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/notification/todo_transaction/test_remove_cache_subscriber.py::TestTodoRemoveCacheSubscriber::test_handle: passed != not found`
- `tests/unit/notification/todo_transaction/test_transaction_log_subscriber.py::TestTransactionLogSubscriber::test_handle: passed != not found`
- `tests/unit/resources/todo/usecases/test_add_todo.py::TestAddTodoUseCase::test_handle_return_success: passed != not found`
- `tests/unit/resources/todo/usecases/test_add_todo.py::TestAddTodoUseCase::test_handle_return_success_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_delete_todo_by_id.py::TestDeleteTodoByIdUseCase::test_handle_return_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_delete_todo_by_id.py::TestDeleteTodoByIdUseCase::test_handle_return_success: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_all.py::TestGetTodoByIdUseCase::test_handle_return_empty_list: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_all.py::TestGetTodoByIdUseCase::test_handle_return_list: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdUseCase::test_handle_return_none_when_data_response_is_none: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdUseCase::test_handle_return_todo: passed != not found`
- `tests/unit/resources/todo/usecases/test_update_todo.py::TestAddTodoUseCase::test_handle_return_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_update_todo.py::TestAddTodoUseCase::test_handle_return_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_add: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_check_connection_is_not_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_check_connection_is_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_delete: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_exist: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_get: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_get_client_throw_exception_when_client_is_none: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 4, cov finished with status 1
### test diff with round premig
- `tests/integration/resources/healt_check/test_health_check_resource.py::TestTodo::test_get: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_add_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_add_todo_should_return_unprocessable_when_invalid_entity: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_delete_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_get_todo_all: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_get_todo_by_id: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_update_todo: passed != not found`
- `tests/integration/resources/todo/test_todo_resource.py::TestTodo::test_update_todo_should_return_unprocessable_when_invalid_entity: passed != not found`
- `tests/unit/data/todo/usecases/test_add_todo_data.py::TestAddTodoDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/data/todo/usecases/test_delete_todo_by_id_data.py::TestDeleteTodoByIdDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/data/todo/usecases/test_delete_todo_by_id_data.py::TestDeleteTodoByIdDataUseCase::test_handle_return_success_false_when_todo_is_not_exist: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_handle_return_empty_list: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_handle_return_list: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_all_data.py::TestGetTodoAllDataUseCase::test_request_cache_parameter: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdDataUseCase::test_handle_return_none_when_todo_is_not_exist: passed != not found`
- `tests/unit/data/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdDataUseCase::test_handle_return_todo: passed != not found`
- `tests/unit/data/todo/usecases/test_update_todo_data.py::TestUpdateTodoDataUseCase::test_handle_return_exception_when_todo_not_found: passed != not found`
- `tests/unit/data/todo/usecases/test_update_todo_data.py::TestUpdateTodoDataUseCase::test_handle_return_success: passed != not found`
- `tests/unit/notification/todo_transaction/test_remove_cache_subscriber.py::TestTodoRemoveCacheSubscriber::test_handle: passed != not found`
- `tests/unit/notification/todo_transaction/test_transaction_log_subscriber.py::TestTransactionLogSubscriber::test_handle: passed != not found`
- `tests/unit/resources/todo/usecases/test_add_todo.py::TestAddTodoUseCase::test_handle_return_success: passed != not found`
- `tests/unit/resources/todo/usecases/test_add_todo.py::TestAddTodoUseCase::test_handle_return_success_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_delete_todo_by_id.py::TestDeleteTodoByIdUseCase::test_handle_return_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_delete_todo_by_id.py::TestDeleteTodoByIdUseCase::test_handle_return_success: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_all.py::TestGetTodoByIdUseCase::test_handle_return_empty_list: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_all.py::TestGetTodoByIdUseCase::test_handle_return_list: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdUseCase::test_handle_return_none_when_data_response_is_none: passed != not found`
- `tests/unit/resources/todo/usecases/test_get_todo_by_id.py::TestGetTodoByIdUseCase::test_handle_return_todo: passed != not found`
- `tests/unit/resources/todo/usecases/test_update_todo.py::TestAddTodoUseCase::test_handle_return_false_when_data_response_is_not_successful: passed != not found`
- `tests/unit/resources/todo/usecases/test_update_todo.py::TestAddTodoUseCase::test_handle_return_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_add: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_check_connection_is_not_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_check_connection_is_success: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_delete: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_exist: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_get: passed != not found`
- `tests/unit/utils/test_cache_provider.py::TestCacheProvider::test_get_client_throw_exception_when_client_is_none: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
