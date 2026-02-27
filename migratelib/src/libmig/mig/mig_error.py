import enum


class ErrorCode(enum.IntEnum):
    INCORRECT_CLI_ARGUMENTS = 1
    PREVIOUS_ROUND_FAILED = 2
    PREVIOUS_ROUND_NOT_DONE = 3
    FAILED_TO_INSTALL_VENV = 4

    UNCOVERED_FILES = 101
    NO_PREMIG_TESTS = 102
    NO_RUNNING_PREMIG_TESTS = 103
    NO_TEST_REPORT_GENERATED = 104
    NO_COV_REPORT_GENERATED = 105

    TOO_MANY_FILES_TO_MIGRATE = 203
    NO_FILES_TO_MIGRATE = 204

    LLM_TOKEN_LIMIT_EXCEEDED = 301
    LLM_API_TIMEOUT = 302
    LLM_NO_RESPONSE = 303
    LLM_MORE_THAN_ONE_RESPONSE = 304
    LLM_UNEXPECTED_FINISH_REASON = 305
    LLM_UNKNOWN_CLIENT = 306

    LLM_SYNTAX_ERROR = 307

    TESTS_RUN_INDEFINITELY = 401


class MigError(Exception):
    """Migration error class"""

    def __init__(self, exit_code: ErrorCode, error_type: str, message: str = None):
        self.error_code = exit_code
        self.error_type = error_type
        self.message = message or error_type
        super().__init__(self.message)
