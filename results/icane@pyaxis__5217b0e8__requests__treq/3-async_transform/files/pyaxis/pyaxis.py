import logging
import re
from numpy import nan
from pandas import Series
import treq
from twisted.internet.defer import ensureDeferred

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
            response = await treq.get(uri, timeout=timeout)
            if response.code != 200:
                raise Exception(f"HTTPError = {response.code} {response.phrase.decode('utf-8')}")
            raw_pcaxis = await response.text(encoding)
        except Exception as e:
            logger.error('Error while fetching URL: %s', str(e))
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
        'TRANSLATION' : translation_dict
    }
    return parsed_pc_axis
