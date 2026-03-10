## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/sann05@python-currencycom__d790bd00__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating currencycom/client.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_client.py::TestClient::test__to_epoch_miliseconds_default: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_default_client_order_id: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_default_order_id: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_24h_price_change_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_24h_price_change_with_symbol: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_info_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_info_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_incorrect_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_incorrect_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_end_time: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_start_and_end_times: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_start_time: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_both_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_both_time_set_exceed_max_range: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_exceed_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_limit_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_only_end_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_only_start_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_exchange_info: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_exceed_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_endTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_startTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_startTime_and_endTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_with_symbol: passed != not found`
- `tests/test_client.py::TestClient::test_get_order_book_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_order_book_with_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_server_time: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_buy: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_limit: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_sell: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_incorrect_limit_no_price: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_incorrect_limit_no_time_in_force: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_not_called: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 52 functions to mark async including 41 tests
- Found 41 calls to await
- 2 files requires transformation
- transforming currencycom/client.py
- transforming tests/test_client.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_client.py::TestClient::test__to_epoch_miliseconds_default: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_default_client_order_id: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_default_order_id: passed != not found`
- `tests/test_client.py::TestClient::test_cancel_order_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_24h_price_change_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_24h_price_change_with_symbol: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_info_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_info_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_incorrect_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_incorrect_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_end_time: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_start_and_end_times: passed != not found`
- `tests/test_client.py::TestClient::test_get_account_trade_list_with_start_time: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_both_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_both_time_set_exceed_max_range: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_exceed_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_limit_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_only_end_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_agg_trades_only_start_time_set: passed != not found`
- `tests/test_client.py::TestClient::test_get_exchange_info: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_exceed_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_max_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_endTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_startTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_klines_with_startTime_and_endTime: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_get_open_orders_with_symbol: passed != not found`
- `tests/test_client.py::TestClient::test_get_order_book_default: passed != not found`
- `tests/test_client.py::TestClient::test_get_order_book_with_limit: passed != not found`
- `tests/test_client.py::TestClient::test_get_server_time: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_buy: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_limit: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_default_sell: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_incorrect_limit_no_price: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_incorrect_limit_no_time_in_force: passed != not found`
- `tests/test_client.py::TestClient::test_new_order_invalid_recv_window: passed != not found`
- `tests/test_client.py::TestClient::test_not_called: passed != not found`
- async_transform finished
