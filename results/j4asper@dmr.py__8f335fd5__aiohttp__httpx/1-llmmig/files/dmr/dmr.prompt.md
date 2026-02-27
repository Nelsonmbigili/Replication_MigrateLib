The following Python code currently uses the library "aiohttp" version 3.9.5.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "aiohttp" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "aiohttp" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from __future__ import annotations
from typing import Optional
from dmr.models import Vehicle
from re import search
from dmr.utils import (
    scrape_async,
    scrape,
    errors,
)


class DMR:

    @classmethod
    def validate_license_plate(cls, license_plate: str) -> bool:
        """Checks if the given string can be a license plate, this check is also run prior to the webscraping.

        Args:
            license_plate (str): The license plate to check

        Returns:
            bool: Returns True if the given license plate could be a license plate, or False if not.
        """

        match = search(r"^[A-ZÆØÅ0-9]{2,7}$", license_plate.upper())
        if match:
            return True
        else:
            return False


    @classmethod
    def get_by_plate(cls, license_plate: str) -> Optional[Vehicle]:
        """Get data from DMR by license plate.

        Args:
            license_plate (str): The license plate to look up. Not required if license plate was passed into the DMR object.

        Raises:
            InvalidLicensePlate: Invalid license plate was given

        Returns:
            DMR: DMR object is returned, check https://github.com/j4asper/dmr.py/wiki for more information.
        """
        
        if not cls.validate_license_plate(license_plate):
            raise errors.InvalidLicensePlate("Invalid license plate. license plate length should be between 2 and 7 letters and/or digits.")

        data = scrape(license_plate=license_plate)
        if data:
            return Vehicle(**data)
        else:
            return None


    @classmethod
    async def get_by_plate_async(cls, license_plate: str) -> Optional[Vehicle]:
        """Get data from DMR asynchronously by license plate.

        Args:
            license_plate (str): The license plate to look up.

        Raises:
            InvalidLicensePlate: Invalid license plate was given

        Returns:
            DMR: DMR object is returned, check https://github.com/j4asper/dmr.py/wiki for more information.
        """

        if not cls.validate_license_plate(license_plate):
            raise errors.InvalidLicensePlate(
                "Invalid license plate. license plate length should be between 2 and 7 letters and/or digits.")

        data = await scrape_async(license_plate=license_plate)
        if data:
            return Vehicle(**data)
        else:
            return None

```