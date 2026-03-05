### Explanation of Changes
To migrate the code from using the `attrs` library to the `cattrs` library, the following changes were made:

1. **Import Statement**: The import statement for `attrs` was replaced with `cattrs`. The `cattrs` library is designed to work with `attrs` and provides additional functionality for serialization and deserialization.
2. **Class Decorators**: The `@attr.attrs` decorator was replaced with `@cattrs` for the classes. This allows `cattrs` to handle the serialization and deserialization of the `attrs` classes.
3. **Serialization Method**: The method `attr.asdict` was replaced with `cattrs.unstructure` to convert the class instances to dictionaries. This is necessary because `cattrs` provides its own way to handle the conversion of `attrs` classes to dictionaries.

Here is the modified code:

```python
from typing import Dict, Optional

import cattrs


@cattrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class SwaggerContact:
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None

    def empty(self) -> bool:
        return self.name is None and self.url is None and self.email is None


@cattrs.define(slots=True, auto_attribs=True, frozen=True, kw_only=True)
class SwaggerLicense:
    name: str
    url: Optional[str] = None


@cattrs.define(slots=True, auto_attribs=True, frozen=False, kw_only=True)
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
            result["contact"] = cattrs.unstructure(self.contact)
        if self.license is not None:
            result["license"] = cattrs.unstructure(self.license)

        return result
```