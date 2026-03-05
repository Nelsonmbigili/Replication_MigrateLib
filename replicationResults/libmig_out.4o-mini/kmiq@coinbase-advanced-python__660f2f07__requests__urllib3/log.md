## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/kmiq@coinbase-advanced-python__660f2f07__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 8 files
### migrating coinbaseadvanced/client.py
### migrating coinbaseadvanced/models/accounts.py
### migrating coinbaseadvanced/models/common.py
### migrating coinbaseadvanced/models/error.py
### migrating coinbaseadvanced/models/fees.py
### migrating coinbaseadvanced/models/orders.py
### migrating coinbaseadvanced/models/portfolios.py
### migrating coinbaseadvanced/models/products.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_cancel_orders_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_buy_market_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_limit_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure_no_funds: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_portfolio_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_sell_market_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_stop_limit_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_delete_portfolio_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_preview_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_portfolio_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_failure: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_best_bid_asks: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_order_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_portfolio_breakdown_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles_all: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_trades: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_transactions_summary: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_unix_time: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_all_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_failure: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_all_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_all_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_with_extra_unnamed_arg_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_portfolios_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_products_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_move_funds_success: passed != failed`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_product_book: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
