from typing import Dict, Optional

import cattrs


@cattrs.define(slots=True, frozen=True, kw_only=True)
class SwaggerContact:
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None

    def empty(self) -> bool:
        return self.name is None and self.url is None and self.email is None


@cattrs.define(slots=True, frozen=True, kw_only=True)
class SwaggerLicense:
    name: str
    url: Optional[str] = None


@cattrs.define(slots=True, frozen=False, kw_only=True)
class SwaggerInfo:
    title: str
    version: str
    description: Optional[str] = None
    terms_of_service: Optional[str] = None
    contact: Optional[SwaggerContact] = None
    license: Optional[SwaggerLicense] = None

    def to_json(self) -> Dict:
        def filter_none(obj):
            """Custom unstructure hook to filter out None values."""
            return {k: v for k, v in cattrs.unstructure(obj).items() if v is not None}

        result: Dict = {
            "title": self.title,
            "version": self.version,
        }
        if self.description is not None:
            result["description"] = self.description
        if self.terms_of_service is not None:
            result["termsOfService"] = self.terms_of_service
        if self.contact is not None and not self.contact.empty():
            result["contact"] = filter_none(self.contact)
        if self.license is not None:
            result["license"] = filter_none(self.license)

        return result
