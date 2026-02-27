The following Python code currently uses the library "attrs" version 25.3.0.
Migrate this code to use the library "cattrs" version 24.1.3 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "attrs" to "cattrs".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "attrs" and "cattrs".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from typing import Dict, Optional

import attr


@attr.attrs(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class SwaggerContact:
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None

    def empty(self) -> bool:
        return self.name is None and self.url is None and self.email is None


@attr.attrs(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class SwaggerLicense:
    name: str
    url: Optional[str] = None


@attr.attrs(slots=True, auto_attribs=True, frozen=False, kw_only=True)
class SwaggerInfo:
    title: str
    version: str
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    contact: Optional[SwaggerContact] = None
    license: Optional[SwaggerLicense] = None

    def to_json(self) -> Dict:
        result: Dict = {
            "title": self.title,
            "version": self.version,
        }
        if self.description is not None:
            result["description"] = self.description
        if self.terms_of_service is not None:
            result["termsOfService"] = self.terms_of_service
        if self.contact is not None and not self.contact.empty():
            result["contact"] = attr.asdict(self.contact, filter=lambda _, y: y is not None)
        if self.license is not None:
            result["license"] = attr.asdict(self.license, filter=lambda _, y: y is not None)

        return result

```