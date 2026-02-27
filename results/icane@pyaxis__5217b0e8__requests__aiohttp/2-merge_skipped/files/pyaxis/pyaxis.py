"""Pcaxis Parser module parses px files into dataframes.

This module obtains a pandas DataFrame of tabular data from a PC-Axis
file or URL. Reads data and metadata from PC-Axis [1]_ into a dataframe and
dictionary. It handles multilingual PX files by letting the user input a language prerequisite. 
Else the process runs on the default language of the PX file. 
The output is a dictionary containing three structures: a dictionary of metadata, a dataframe, and a translation dictionary for the metadata fields (which is empty is the PX file is only in 1 language).

Example:
    from pyaxis import pyaxis

    px = pyaxis.parse(self.base_path + 'px/2184.px', encoding='ISO-8859-2')

.. [1] https://www.scb.se/en/services/statistical-programs-for-px-files/

..todo::

    meta_split: "NOTE" attribute can be multiple, but only the last one
    is added to the dictionary.

"""

import logging
import re
from numpy import nan
from pandas import Series
import aiohttp  # Replaced requests with aiohttp
import asyncio  # Required for asynchronous operations
from pyaxis.metadata_processing import metadata_extract, metadata_split_to_dict, multilingual_parse
from pyaxis.data_processing import get_dimensions, build_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def uri_type(uri):
    """Determine the type of URI.

       Args:
         uri (str): pc-axis file name or URL
       Returns:
         uri_type_result (str): 'URL' | 'FILE'

    ..  Regex debugging:
        https://pythex.org/

    """
    uri_type_result = 'FILE'

    # django url validation regex:
    regex = re.compile(r'^(?:http|ftp)s?://'  # http:// or https://
                       # domain...
                       r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
                       r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                       r'localhost|'  # localhost...
                       r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                       r'(?::\d+)?'  # optional port
                       r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if re.match(regex, uri):
        uri_type_result = 'URL'

    return uri_type_result


async def read(uri, encoding, timeout=10):
    """Read a text file from file system or URL.

    Args:
        uri (str): file name or URL
        encoding (str): charset encoding
        timeout (int): request timeout; optional

    Returns:
        raw_pcaxis (str): file contents.

    """
    raw_pcaxis = ''

    if uri_type(uri) == 'URL':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(uri, timeout=timeout) as response:
                    response.raise_for_status()
                    response_text = await response.text(encoding=encoding)
                    raw_pcaxis = response_text
        except aiohttp.ClientConnectorError as connect_error:
            logger.error('ConnectionError = %s', str(connect_error))
            raise
        except aiohttp.ClientResponseError as http_error:
            logger.error('HTTPError = %s',
                         str(http_error.status) + ' ' +
                         http_error.message)
            raise
        except aiohttp.InvalidURL as url_error:
            logger.error('URLError = %s', str(url_error))
            raise
        except asyncio.TimeoutError as timeout_error:
            logger.error('ConnectionTimeout = %s', str(timeout_error))
            raise
        except Exception:
            import traceback
            logger.error('Generic exception: %s', traceback.format_exc())
            raise
    else:  # file parsing
        file_object = open(uri, encoding=encoding)
        raw_pcaxis = file_object.read()
        file_object.close()

    return raw_pcaxis


async def parse(uri, encoding, timeout=10,
                null_values=r'^"\."$', sd_values=r'"\.\."',
                lang=None):
    """Extract metadata and data sections from pc-axis.

    Args:
        uri (str): file name or URL
        encoding (str): charset encoding
        timeout (int): request timeout in seconds; optional
        null_values(str): regex with the pattern for the null values in the px
                          file. Defaults to '.'.
        sd_values(str): regex with the pattern for the statistical disclosured
                        values in the px file. Defaults to '..'.
        lang: language desired for the metadata and the column names of the dataframe

    Returns:
         pc_axis_dict (dictionary): dictionary of metadata and pandas df.
                                    METADATA: dictionary of metadata
                                    DATA: pandas dataframe
                                    TRANSLATION: dictionary of translations of the metadata (empty if the px file is monolingual)

    """
    # get file content or URL stream
    try:
        pc_axis = await read(uri, encoding, timeout)
    except ValueError:
        import traceback
        logger.error('Generic exception: %s', traceback.format_exc())
        raise

    # metadata and data extraction and cleaning
    metadata_elements, raw_data = metadata_extract(pc_axis)

    # stores raw metadata into a dictionary
    metadata = metadata_split_to_dict(metadata_elements)

    # handles the languages of the px file
    metadata, translation_dict = multilingual_parse(metadata, lang)

    # explode raw data into a Series of values, which can contain nullos or sd
    # (statistical disclosure)
    data_values = Series(raw_data.split())

    # extract dimension names and members from
    # 'meta_dict' STUB and HEADING keys
    dimension_names, dimension_members = get_dimensions(metadata)

    # build a dataframe
    df = build_dataframe(
        dimension_names,
        dimension_members,
        data_values,
        null_values=null_values,
        sd_values=sd_values)

    # dictionary of metadata and data (pandas dataframe)
    parsed_pc_axis = {
        'METADATA': metadata,
        'DATA': df,
        'TRANSLATION': translation_dict
    }
    return parsed_pc_axis