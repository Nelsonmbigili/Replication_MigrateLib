To migrate the provided code from using the `requests` library to the `aiohttp` library, several changes are necessary:

1. **Asynchronous Context**: The `aiohttp` library is designed for asynchronous programming, so we need to use `async` and `await` keywords. This means that the functions that perform HTTP requests must be defined as asynchronous functions.
  
2. **Session Management**: In `aiohttp`, we need to create an `aiohttp.ClientSession` to manage connections. This session should be used to make requests, and it is best practice to use it within an asynchronous context manager.

3. **Making Requests**: The method to make a GET request changes from `requests.get(url)` to `session.get(url)`, and we need to await the response.

4. **Reading Response Content**: Instead of accessing `.content` directly, we need to await the `.text()` or `.read()` method on the response object to get the response body.

5. **Error Handling**: While not explicitly required, it is good practice to handle exceptions that may arise from network requests.

Here is the modified code using `aiohttp`:

```python
import os
import warnings
import numpy as np
import aiohttp
import xarray as xr
import xmltodict
import asyncio


def _get_angle_values(values_list: dict, angle: str) -> np.ndarray:
    """Gets the angle values per detector in Sentinel-2 granule metadata.

    Parameters
    ----------
    values_list : dict
        Dictionary of angle values in the metadata.
    angle : str
        Angle to retrieve. Either 'Zenith' oder 'Azimuth'.

    Returns
    -------
    numpy.ndarray
        Angle values per detector.
    """
    values = values_list[angle]["Values_List"]["VALUES"]
    array = np.array([row.split(" ") for row in values]).astype(float)

    return array


async def angles_from_metadata(metadata: str) -> xr.DataArray:
    """Gets the angle values per band (and Sun) in Sentinel-2 granule metadata.

    The angle values are retrieved for the Sun and View modes as a
    :code:`xarray.DataArray` with a shape (band, angle, y, x).

    Parameters
    ----------
    metadata : str
        Path to the metadata file. An URL can also be used.

    Returns
    -------
    xarray.DataArray
        Angle values per band and Sun.
    """
    # Convert the xml into a dict
    if os.path.exists(metadata):
        data = xmltodict.parse(open(metadata, "r").read())
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata) as response:
                response_text = await response.text()
                data = xmltodict.parse(response_text)

    # Extract the geocoding and angles, all the stuff we need is here
    Tile_Geocoding = data["n1:Level-2A_Tile_ID"]["n1:Geometric_Info"]["Tile_Geocoding"]
    Tile_Angles = data["n1:Level-2A_Tile_ID"]["n1:Geometric_Info"]["Tile_Angles"]

    # Save the upper left corner for the array
    ULX = float(Tile_Geocoding["Geoposition"][0]["ULX"])
    ULY = float(Tile_Geocoding["Geoposition"][0]["ULY"])

    # Band names
    band_names = ["B" + f"0{x}"[-2:] for x in np.arange(1, 13)]
    band_names.insert(8, "B8A")

    # Angles to work with
    ANGLES = ["Zenith", "Azimuth"]

    # Create a dictionary to store the angles per band (and the Sun)
    bands_dict = dict()
    for key in ["Sun"] + band_names:
        bands_dict[key] = dict(Zenith=list(), Azimuth=list())

    # Each band has multiple detectors, so we have to go through all of them
    # and save them in a list to later do a nanmean
    for single_angle_detector in Tile_Angles["Viewing_Incidence_Angles_Grids"]:
        band_id = int(single_angle_detector["@bandId"])
        band_name = band_names[band_id]
        for angle in ANGLES:
            bands_dict[band_name][angle].append(
                _get_angle_values(single_angle_detector, angle)
            )

    # Do the same for the Sun, but there is just one, of course, duh
    for angle in ANGLES:
        bands_dict["Sun"][angle].append(
            _get_angle_values(Tile_Angles["Sun_Angles_Grid"], angle)
        )

    # Do the nanmean of the detectors angles per band
    for key, value in bands_dict.items():
        for angle in ANGLES:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                bands_dict[key][angle] = np.nanmean(
                    np.array(bands_dict[key][angle]), axis=0
                )
        bands_dict[key] = np.array(
            [bands_dict[key]["Zenith"], bands_dict[key]["Azimuth"]]
        )

    # x and y coordinates of the array to create
    y = np.arange(ULY, ULY - 5000 * 23, -5000) - 2500
    x = np.arange(ULX, ULX + 5000 * 23, 5000) + 2500

    # Create the array
    try:
        da = xr.DataArray(
            list(bands_dict.values()),
            dims=["band", "angle", "y", "x"],
            coords=dict(band=list(bands_dict.keys()), angle=ANGLES, x=x, y=y),
        )
    except ValueError:
        raise ValueError("Not all bands include angles values.")

    # Add attributes
    da.attrs["epsg"] = Tile_Geocoding["HORIZONTAL_CS_CODE"]

    return da


async def get_processing_baseline(metadata: str) -> float:
    """Gets the processing baseline in Sentinel-2 user metadata.

    The processing baseline is retrieved as a float.

    Parameters
    ----------
    metadata : str
        Path to the metadata file. An URL can also be used.

    Returns
    -------
    float
        Processing baseline.
    """
    # Convert the xml into a dict
    if os.path.exists(metadata):
        data = xmltodict.parse(open(metadata, "r").read())
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(metadata) as response:
                response_text = await response.text()
                data = xmltodict.parse(response_text)

    # Get the processing baseline
    PROCESSING_BASELINE = data["n1:Level-2A_User_Product"]["n1:General_Info"][
        "Product_Info"
    ]["PROCESSING_BASELINE"]

    return float(PROCESSING_BASELINE)
```

In this modified code, the functions `angles_from_metadata` and `get_processing_baseline` are now asynchronous, and they utilize `aiohttp` for making HTTP requests. The overall structure and logic of the code remain unchanged, adhering to the original coding style.