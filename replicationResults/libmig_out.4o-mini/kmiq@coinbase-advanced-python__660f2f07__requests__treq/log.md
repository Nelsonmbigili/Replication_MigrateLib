## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/kmiq@coinbase-advanced-python__660f2f07__requests__treq/.venv
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
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_cancel_orders_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_client_creation_should_pass: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_buy_market_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_limit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure_no_funds: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_sell_market_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_stop_limit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_delete_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_preview_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_best_bid_asks: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_portfolio_breakdown_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles_all: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_trades: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_transactions_summary: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_unix_time: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_with_extra_unnamed_arg_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_portfolios_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_products_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_move_funds_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_product_book: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_cancel_orders_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_client_creation_should_pass: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_buy_market_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_limit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_order_failure_no_funds: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_sell_market_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_create_stop_limit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_delete_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_preview_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_edit_portfolio_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_account_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_best_bid_asks: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_order_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_portfolio_breakdown_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_candles_all: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_product_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_trades: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_transactions_summary: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_get_unix_time: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_failure: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_accounts_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_fills_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_all_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_orders_with_extra_unnamed_arg_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_portfolios_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_list_products_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_move_funds_success: passed != not found`
- `tests/test_client.py::TestCoinbaseAdvancedTradeAPIClient::test_product_book: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
