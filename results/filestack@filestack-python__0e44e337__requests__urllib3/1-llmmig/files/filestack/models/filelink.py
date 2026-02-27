import json
from urllib3 import PoolManager
from urllib3.request import urlencode
from urllib3.filepost import encode_multipart_formdata
from filestack import config
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin


class Filelink(ImageTransformationMixin, CommonMixin):
    """
    Filelink object represents a file that whas uploaded to Filestack.
    A filelink object can be created by uploading a file using Client instance,
    or by initializing Filelink class with a handle (unique id) of already uploaded file.

    >>> from filestack import Filelink
    >>> flink = Filelink('sm9IEXAMPLEQuzfJykmA')
    >>> flink.url
    'https://cdn.filestackcontent.com/sm9IEXAMPLEQuzfJykmA'
    """
    def __init__(self, handle, apikey=None, security=None, upload_response=None):
        """
        Args:
            handle (str): The path of the file to wrap
            apikey (str): Filestack API key that may be required for some API calls
            security (:class:`filestack.Security`): Security object that will be used by default
               for all API calls
        """
        self.apikey = apikey
        self.handle = handle
        self.security = security
        self.upload_response = upload_response
        self.http = PoolManager()

    def __repr__(self):
        return '<Filelink {}>'.format(self.handle)

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle]
        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)

    def metadata(self, attributes_list=None, security=None):
        """
        Retrieves filelink's metadata.

        Args:
            attributes_list (list): list of attributes that you wish to receive. When not provided,
                default set of parameters will be returned (may differ depending on your storage settings)
            security (:class:`filestack.Security`): Security object that will be used
                to retrieve metadata

        >>> filelink.metadata(['size', 'filename'])
        {'filename': 'envelope.jpg', 'size': 171832}

        Returns:
            `dict`: A buffered writable file descriptor
        """
        attributes_list = attributes_list or []
        params = {}
        for item in attributes_list:
            params[item] = 'true'
        sec = security or self.security
        if sec is not None:
            params.update({'policy': sec.policy_b64, 'signature': sec.signature})
        url = self._build_url(security=sec) + '/metadata'
        response = self.http.request('GET', url, fields=params)
        return json.loads(response.data.decode('utf-8'))

    def delete(self, apikey=None, security=None):
        """
        Deletes filelink.

        Args:
            apikey (str): Filestack API key that will be used for this API call
            security (:class:`filestack.Security`): Security object that will be used
                to delete filelink

        Returns:
            None
        """
        sec = security or self.security
        apikey = apikey or self.apikey

        if sec is None:
            raise Exception('Security is required to delete filelink')

        if apikey is None:
            raise Exception('Apikey is required to delete filelink')

        url = '{}/file/{}'.format(config.API_URL, self.handle)
        delete_params = {
            'key': apikey,
            'policy': sec.policy_b64,
            'signature': sec.signature
        }
        self.http.request('DELETE', url, fields=delete_params)

    def overwrite(self, *, filepath=None, url=None, file_obj=None, base64decode=False, security=None):
        """
        Overwrites filelink with new content

        Args:
            filepach (str): path to file
            url (str): file URL
            file_obj (io.BytesIO or similar): file-like object
            base64decode (bool): indicates if content should be decoded before it is stored
            security (:class:`filestack.Security`): Security object that will be used
                to overwrite filelink

        Note:
            This method accepts keyword arguments only.
            Out of filepath, url and file_obj only one should be provided.
        """
        sec = security or self.security
        if sec is None:
            raise Exception('Security is required to overwrite filelink')
        req_params = {
            'policy': sec.policy_b64,
            'signature': sec.signature,
            'base64decode': str(base64decode).lower()
        }

        request_url = '{}/file/{}'.format(config.API_URL, self.handle)
        if url:
            encoded_data = urlencode({'url': url})
            self.http.request('POST', request_url, fields=req_params, body=encoded_data)
        elif filepath:
            with open(filepath, 'rb') as f:
                files = {'fileUpload': ('filename', f, 'application/octet-stream')}
                encoded_data, content_type = encode_multipart_formdata(files)
                headers = {'Content-Type': content_type}
                self.http.request('POST', request_url, fields=req_params, body=encoded_data, headers=headers)
        elif file_obj:
            files = {'fileUpload': ('filename', file_obj, 'application/octet-stream')}
            encoded_data, content_type = encode_multipart_formdata(files)
            headers = {'Content-Type': content_type}
            self.http.request('POST', request_url, fields=req_params, body=encoded_data, headers=headers)
        else:
            raise Exception('filepath, file_obj or url argument must be provided')

        return self
