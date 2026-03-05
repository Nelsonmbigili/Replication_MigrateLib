## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/pymike00@tinychat__cade1f91__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 12 files
### migrating tests/llms/test_anthropic_client.py
### migrating tests/llms/test_cohere_client.py
### migrating tests/llms/test_google_client.py
### migrating tests/llms/test_mistral_client.py
### migrating tests/llms/test_openai_client.py
### migrating tests/llms/test_together_client.py
### migrating tinychat/llms/anthropic.py
### migrating tinychat/llms/cohere.py
### migrating tinychat/llms/google.py
### migrating tinychat/llms/mistral.py
### migrating tinychat/llms/openai.py
### migrating tinychat/llms/together.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/llms/test_anthropic_client.py::TestAnthropicAIClientStreaming::test_perform_stream_request_failure: passed != failed`
- `tests/llms/test_anthropic_client.py::TestAnthropicAIClientStreaming::test_perform_stream_request_success: passed != failed`
- `tests/llms/test_cohere_client.py::TestCohereClientStreaming::test_perform_stream_request_failure: passed != failed`
- `tests/llms/test_cohere_client.py::TestCohereClientStreaming::test_perform_stream_request_success: passed != failed`
- `tests/llms/test_mistral_client.py::TestMistralClientStreaming::test_perform_stream_request_failure: passed != failed`
- `tests/llms/test_mistral_client.py::TestMistralClientStreaming::test_perform_stream_request_success: passed != failed`
- `tests/llms/test_openai_client.py::TestOpenAIClientStreaming::test_perform_stream_request_failure: passed != failed`
- `tests/llms/test_openai_client.py::TestOpenAIClientStreaming::test_perform_stream_request_success: passed != failed`
- `tests/llms/test_together_client.py::TestTogetherClientStreaming::test_perform_stream_request_failure: passed != failed`
- `tests/llms/test_together_client.py::TestTogetherClientStreaming::test_perform_stream_request_success: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
