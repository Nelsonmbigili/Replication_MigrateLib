from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AuthResult:
    """
    Contains the result of authentication, to be returned to the smtp_AUTH method.
    All initialization arguments _must_ be keyworded!
    """

    success: bool
    """Indicates authentication is successful or not"""

    handled: bool = True
    """
    True means everything (including sending of status code) has been handled by the
    AUTH handler and smtp_AUTH should not do anything else.
    Applicable only if success == False.
    """

    message: Optional[str] = None
    """
    Optional message for additional handling by smtp_AUTH.
    Applicable only if handled == False.
    """

    auth_data: Optional[Any] = field(default=None, repr=lambda x: "...")
    """
    Optional free-form authentication data. For the built-in mechanisms, it is usually
    an instance of LoginPassword. Other implementations are free to use any data
    structure here.
    """
