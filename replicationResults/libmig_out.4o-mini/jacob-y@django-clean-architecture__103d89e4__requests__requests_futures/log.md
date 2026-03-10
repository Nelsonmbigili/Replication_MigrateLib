## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/jacob-y@django-clean-architecture__103d89e4__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating modules/Application/PluginAdaptors/HTTPMixin.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_capture: passed != not found`
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_create: passed != not found`
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_status: passed != not found`
- `tests/Unit/Application/test_stripe_adaptor.py::StripeAdaptorTest::test_card: passed != not found`
- `tests/Unit/Domain/test_paypal_service.py::PayPalServiceTest::test_capture: passed != not found`
- `tests/Unit/Domain/test_paypal_service.py::PayPalServiceTest::test_pay: passed != not found`
- `tests/Unit/Domain/test_paypal_service.py::PayPalServiceTest::test_status: passed != not found`
- `tests/Unit/Domain/test_stripe_service.py::StripeServiceTest::test_capture: passed != not found`
- `tests/Unit/Domain/test_stripe_service.py::StripeServiceTest::test_pay: passed != not found`
- `tests/Unit/Domain/test_stripe_service.py::StripeServiceTest::test_status: passed != not found`
- `tests/Unit/Entities/test_card.py::CardTest::test_invalid_card_number: passed != not found`
- `tests/Unit/Entities/test_card.py::CardTest::test_invalid_card_year: passed != not found`
- `tests/Unit/Entities/test_card.py::CardTest::test_valid_card: passed != not found`
- `tests/Unit/Entities/test_payment.py::PaymentTest::test_amount_too_high: passed != not found`
- `tests/Unit/Entities/test_payment.py::PaymentTest::test_card_invalid_numbers: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
