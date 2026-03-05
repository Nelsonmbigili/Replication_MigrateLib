from typing import Dict, Union

import cattrs


@cattrs.define(slots=True)
class ValidatorError(Exception):
    error: Union[str, Dict]


class DiscriminatorValidationError(Exception):
    pass
