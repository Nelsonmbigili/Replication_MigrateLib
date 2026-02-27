import filestack.models
import pycurl
import json
from io import BytesIO


class AudioVisual:

    def __init__(self, url, uuid, timestamp, apikey=None, security=None):
        """
        AudioVisual instances provide a bridge between transform and filelinks, and allow
        you to check the status of a conversion and convert to a Filelink once completed

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='path/to/file/doom.mp4')
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)

        filelink = av_convert.to_filelink()
        print(filelink.url)
        ```
        """
        self.url = url
        self.apikey = apikey
        self.security = security
        self.uuid = uuid
        self.timestamp = timestamp

    def to_filelink(self):
        """
        Checks is the status of the conversion is complete and, if so, converts to a Filelink

        *returns* [Filestack.Filelink]

        ```python
        filelink = av_convert.to_filelink()
        ```
        """
        if self.status != 'completed':
            raise Exception('Audio/video conversion not complete!')

        response = self._make_get_request(self.url)
        handle = response['data']['url'].split('/')[-1]
        return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

    @property
    def status(self):
        """
        Returns the status of the AV conversion (makes a GET request)

        *returns* [String]

        ```python
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)
        ```
        """
        response = self._make_get_request(self.url)
        return response['status']

    def _make_get_request(self, url):
        """
        Helper method to perform a GET request using pycurl and return the JSON response.

        :param url: The URL to send the GET request to.
        :return: Parsed JSON response as a dictionary.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.FOLLOWLOCATION, True)  # Follow redirects if necessary
        curl.perform()
        curl.close()

        # Decode the response and parse it as JSON
        response_body = buffer.getvalue().decode('utf-8')
        return json.loads(response_body)
