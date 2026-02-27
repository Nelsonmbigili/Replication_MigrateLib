from typing import Dict, Union

import cattrs


@cattrs.attrs(slots=True, auto_attribs=True)
class ValidatorError(Exception):
    error: Union[str, Dict]


class DiscriminatorValidationError(Exception):
    pass
