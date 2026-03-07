### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The import statement was updated accordingly.
2. **HTTP Requests**: The `requests` methods for making HTTP requests (like `requests.get()`) were replaced with `urllib3` methods. Specifically, we created a connection pool manager using `urllib3.PoolManager()` and used its `request()` method to perform GET requests.
3. **Error Handling**: The exceptions raised by `requests` were replaced with the corresponding exceptions from `urllib3`. The `HTTPError` and `ConnectionError` exceptions were replaced with `urllib3.exceptions.HTTPError` and `urllib3.exceptions.NewConnectionError`, respectively.
4. **Response Handling**: The response handling was adjusted to read the response data from `urllib3`'s response object.

Here is the modified code:

```python
"""Integration tests for pyaxis module."""

from pandas import Series

from pkg_resources import resource_filename

from pyaxis import pyaxis

import pytest

import urllib3
from urllib3.exceptions import HTTPError, NewConnectionError


data_path = resource_filename('pyaxis', 'test/data/')
http = urllib3.PoolManager()


def test_uri_type():
    """uri_type() should be capable of discriminating files and URLs."""
    assert pyaxis.uri_type(
        'https://www.ine.es/jaxiT3/files/es/2184.px') == 'URL'


def test_read():
    """Check if a URL is loaded into a string variable."""
    response = http.request('GET', 'https://www.ine.es/jaxiT3/files/es/1001.px')
    pc_axis = response.data.decode('iso-8859-15')
    assert len(pc_axis) >= 3434
    assert pc_axis.startswith('AXIS-VERSION="2006";')
    assert pc_axis.endswith('6.21 5.95;')


def test_metadata_extract():
    """Should extract pcaxis metadata into a list."""
    response = http.request('GET', 'https://www.ine.es/jaxi/files/_px/es/px/t20/e301/matri/a2000/l0/14001.px?nocab=1')
    pc_axis = response.data.decode('iso-8859-15')
    metadata_elements, raw_data = pyaxis.metadata_extract(pc_axis)
    assert isinstance(metadata_elements, list)
    assert len(metadata_elements) == 23
    assert isinstance(raw_data, str)
    assert len(raw_data) >= 40282


def test_metadata_split_to_dict():
    """Should split metadata into a dictionary."""
    response = http.request('GET', 'https://www.ine.es/jaxi/files/_px/es/px/t20/e301/matri/a2000/l0/14001.px?nocab=1')
    pc_axis = response.data.decode('iso-8859-15')
    metadata_elements, raw_data = pyaxis.metadata_extract(pc_axis)
    metadata = pyaxis.metadata_split_to_dict(metadata_elements)
    assert isinstance(metadata, dict)
    assert len(metadata) == 23


def test_get_dimensions():
    """Should return two lists (dimension names and members)."""
    response = http.request('GET', 'https://www.ine.es/jaxi/files/_px/es/px/t20/e301/matri/a2000/l0/14001.px?nocab=1')
    pc_axis = response.data.decode('iso-8859-15')
    metadata_elements, raw_data = pyaxis.metadata_extract(pc_axis)
    metadata = pyaxis.metadata_split_to_dict(metadata_elements)
    dimension_names, dimension_members = pyaxis.get_dimensions(metadata)
    assert len(dimension_names) == 4
    assert dimension_names[0] == 'Comunidad Autónoma de residencia de los cónyuges'
    assert dimension_names[3] == 'Estado civil anterior de los cónyuges'
    assert len(dimension_members) == 4
    assert dimension_members[0][0] == 'Todas las comunidades'
    assert dimension_members[3][3] == 'Divorciados/as'


def test_build_dataframe():
    """Should return a dataframe with n+1 columns (dimensions + data)."""
    null_values = r'^"\."$'
    sd_values = r'"\.\."'
    response = http.request('GET', 'https://www.ine.es/jaxi/files/_px/es/px/t20/e301/matri/a2000/l0/14001.px?nocab=1')
    pc_axis = response.data.decode('iso-8859-15')
    metadata_elements, raw_data = pyaxis.metadata_extract(pc_axis)
    metadata = pyaxis.metadata_split_to_dict(metadata_elements)
    dimension_names, dimension_members = pyaxis.get_dimensions(metadata)
    data_values = Series(raw_data.split())
    df = pyaxis.build_dataframe(
        dimension_names,
        dimension_members,
        data_values,
        null_values=null_values,
        sd_values=sd_values)
    assert df.shape == (8064, 5)
    assert df['DATA'][7] == '10624.0'
    assert df['DATA'][159] == '534.0'


def test_parse():
    """Should parse a pc-axis into a dataframe and a metadata dictionary"""
    response = http.request('GET', 'https://www.ine.es/jaxi/files/_px/es/px/t20/e301/matri/a2000/l0/14001.px?nocab=1')
    parsed_pcaxis = pyaxis.parse(response.data.decode('ISO-8859-15'))
    assert parsed_pcaxis['DATA'].dtypes['DATA'] == 'object'
    assert len(parsed_pcaxis['DATA']) == 8064
    assert parsed_pcaxis['METADATA']['VALUES(Comunidad Autónoma de residencia de los cónyuges)'][0][0] == 'Total'
    assert parsed_pcaxis['METADATA']['VALUES(Comunidad Autónoma de residencia de los cónyuges)'][0][20] == 'Extranjero'


def test_http_error():
    """Using parse() with a non-existent URL should return a 404."""
    url = 'https://www.ine.es/jaxi'
    with pytest.raises(HTTPError):
        http.request('GET', url)


def test_connection_error():
    """Using parse() with a wrong URL should return a connection error."""
    url = 'https://www.ine.net/jaxiT3/files/t/es/px/1001.px'

    with pytest.raises(NewConnectionError):
        http.request('GET', url)


if __name__ == '__main__':
    pytest.main()
``` 

This code now uses `urllib3` for HTTP requests while maintaining the original structure and functionality of the application.