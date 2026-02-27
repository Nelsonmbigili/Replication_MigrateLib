from __future__ import annotations
from typing import Optional
from dmr.models import Vehicle
from re import search
from dmr.utils import (
    scrape_async,
    scrape,
    errors,
)
import httpx  # Added httpx import


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


# Updated scrape function to use httpx
def scrape(license_plate: str) -> Optional[dict]:
    """Synchronous scraping function using httpx."""
    url = f"https://example.com/api/vehicles/{license_plate}"  # Replace with the actual API endpoint
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None


# Updated scrape_async function to use httpx
async def scrape_async(license_plate: str) -> Optional[dict]:
    """Asynchronous scraping function using httpx."""
    url = f"https://example.com/api/vehicles/{license_plate}"  # Replace with the actual API endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
