## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/paytmmoney@pypmclient__8f966de0__httpx__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating pmClient/apiService.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_apiService.py::test_api_call_helper_400: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_401: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_404: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_415: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_500: passed != failed`
- `tests/test_pmClient.py::test_convert_order_attribute: passed != failed`
- `tests/test_pmClient.py::test_funds_summary_attribute: passed != failed`
- `tests/test_pmClient.py::test_funds_summary_connection: passed != failed`
- `tests/test_pmClient.py::test_generate_session_access_token: passed != failed`
- `tests/test_pmClient.py::test_generate_tpin_attribute: passed != failed`
- `tests/test_pmClient.py::test_generate_tpin_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt__aggregate_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_instruction_id_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_instruction_id_v2_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_status_or_id_attribute: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_status_or_id_v2_attribute: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_expiry_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_v2_connection: passed != failed`
- `tests/test_pmClient.py::test_get_option_chain: passed != failed`
- `tests/test_pmClient.py::test_get_option_chain_config: passed != failed`
- `tests/test_pmClient.py::test_get_user_details_connection: passed != failed`
- `tests/test_pmClient.py::test_holdings_value_connection: passed != failed`
- `tests/test_pmClient.py::test_live_market_data: passed != failed`
- `tests/test_pmClient.py::test_order_book_connection: passed != failed`
- `tests/test_pmClient.py::test_order_margin_connection: passed != failed`
- `tests/test_pmClient.py::test_orders_connection: passed != failed`
- `tests/test_pmClient.py::test_position_connection: passed != failed`
- `tests/test_pmClient.py::test_position_details_connection: passed != failed`
- `tests/test_pmClient.py::test_status_attribute: passed != failed`
- `tests/test_pmClient.py::test_status_connection: passed != failed`
- `tests/test_pmClient.py::test_trade_details_connection: passed != failed`
- `tests/test_pmClient.py::test_update_gtt_attribute: passed != failed`
- `tests/test_pmClient.py::test_update_gtt_v2_attribute: passed != failed`
- `tests/test_pmClient.py::test_user_holdings_data_connection: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 118 functions to mark async including 82 tests
- Found 117 calls to await
- 4 files requires transformation
- transforming tests/test_pmClient.py
- transforming tests/test_apiService.py
- transforming pmClient/pmClient.py
- transforming pmClient/apiService.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_apiService.py::test_api_call_helper_200: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_200_security_master: passed != failed`
- `tests/test_apiService.py::test_api_call_helper_401: passed != failed`
- `tests/test_pmClient.py::test_funds_summary_attribute: passed != failed`
- `tests/test_pmClient.py::test_generate_tpin_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt__aggregate_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_status_or_id_attribute: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_by_status_or_id_v2_attribute: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_expiry_connection: passed != failed`
- `tests/test_pmClient.py::test_get_gtt_v2_connection: passed != failed`
- `tests/test_pmClient.py::test_get_option_chain: passed != failed`
- `tests/test_pmClient.py::test_get_option_chain_config: passed != failed`
- `tests/test_pmClient.py::test_get_user_details_connection: passed != failed`
- `tests/test_pmClient.py::test_holdings_value_connection: passed != failed`
- `tests/test_pmClient.py::test_live_market_data: passed != failed`
- `tests/test_pmClient.py::test_order_book_connection: passed != failed`
- `tests/test_pmClient.py::test_order_margin_connection: passed != failed`
- `tests/test_pmClient.py::test_orders_connection: passed != failed`
- `tests/test_pmClient.py::test_position_connection: passed != failed`
- `tests/test_pmClient.py::test_status_connection: passed != failed`
- `tests/test_pmClient.py::test_trade_details_connection: passed != failed`
- `tests/test_pmClient.py::test_user_holdings_data_connection: passed != failed`
- async_transform finished
