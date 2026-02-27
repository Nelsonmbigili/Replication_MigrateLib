### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: The `requests` module from `filestack.utils` was replaced with `requests_futures.sessions.FuturesSession`.
2. **Session Initialization**: A `FuturesSession` object was created to handle asynchronous requests.
3. **Request Handling**: The `requests.get` call in the `zip` method was replaced with `session.get` from the `FuturesSession` object. Since `requests_futures` returns a `Future` object, the `.result()` method was used to retrieve the actual response synchronously (to maintain the original behavior).
4. **No Other Changes**: The rest of the code remains unchanged, as the migration only affects the way HTTP requests are made.

### Modified Code
```python
import filestack.models
from filestack import config
from filestack.uploads.external_url import upload_external_url
from filestack.trafarets import STORE_LOCATION_SCHEMA, STORE_SCHEMA
from filestack import utils
from requests_futures.sessions import FuturesSession
from filestack.uploads import intelligent_ingestion
from filestack.uploads.multipart import multipart_upload


class Client:
    """
    This class is responsible for uploading files (creating Filelinks),
    converting external urls to Transformation objects, taking url screenshots
    and returning zipped files (multiple Filelinks).

    In order to create a client instance, pass in your Filestack API key.
    You can also specify which storage should be used for your uploads
    and provide a Security object to sign all your API calls.

    >>> from filestack import Client, Security
    >>> security = Security(policy={'expiry': 1594200833}, secret='YOUR APP SECRET')
    >>> cli = Client('<FILESTACK_APIKEY>', storage='gcs', security=security)
    """
    def __init__(self, apikey, storage='S3', security=None):
        """
        Args:
            apikey (str): your Filestack API key
            storage (str): default storage to be used for uploads (one of S3, `gcs`, dropbox, azure)
            security (:class:`filestack.Security`): Security object that will be used by default
                for all API calls
        """
        self.apikey = apikey
        self.security = security
        STORE_LOCATION_SCHEMA.check(storage)
        self.storage = storage
        self.session = FuturesSession()  # Initialize FuturesSession for async requests

    def transform_external(self, external_url):
        """
        Turns an external URL into a Filestack Transformation object

        >>> t_obj = client.transform_external('https://image.url')
        >>> t_obj.resize(width=800)  # now you can do this

        Args:
            external_url (str): file URL

        Returns:
            :class:`filestack.Transformation`
        """
        return filestack.models.Transformation(apikey=self.apikey, security=self.security, external_url=external_url)

    def urlscreenshot(self, url, agent=None, mode=None, width=None, height=None, delay=None):
        """
        Takes a 'screenshot' of the given URL

        Args:
            url (str): website URL
            agent (str): one of: :data:`"desktop"` :data:`"mobile"`
            mode (str): one of: :data:`"all"` :data:`"window"`
            width (int): screen width
            height (int): screen height

        Returns:
            :class:`filestack.Transformation`
        """
        params = locals()
        params.pop('self')
        params.pop('url')

        params = {k: v for k, v in params.items() if v is not None}

        url_task = utils.return_transform_task('urlscreenshot', params)

        new_transform = filestack.models.Transformation(
            self.apikey, security=self.security, external_url=url
        )
        new_transform._transformation_tasks.append(url_task)

        return new_transform

    def zip(self, destination_path, files, security=None):
        """
        Takes array of handles and downloads a compressed ZIP archive
        to provided path

        Args:
            destination_path (str): path where the ZIP file should be stored
            file (list): list of filelink handles and/or URLs
            security (:class:`filestack.Security`): Security object that will be used
                for this API call

        Returns:
            int: ZIP archive size in bytes
        """
        url_parts = [config.CDN_URL, self.apikey, 'zip', '[{}]'.format(','.join(files))]
        sec = security or self.security
        if sec is not None:
            url_parts.insert(3, sec.as_url_string())
        zip_url = '/'.join(url_parts)
        total_bytes = 0
        with open(destination_path, 'wb') as f:
            # Use FuturesSession to make the GET request
            future_response = self.session.get(zip_url, stream=True)
            response = future_response.result()  # Wait for the response (synchronous behavior)
            for chunk in response.iter_content(5 * 1024 ** 2):
                f.write(chunk)
                total_bytes += len(chunk)

        return total_bytes

    def upload_url(self, url, store_params=None, security=None):
        """
        Uploads file from external url

        Args:
            url (str): file URL
            store_params (dict): store parameters to be used during upload
            security (:class:`filestack.Security`): Security object that will be used for this API call

        Returns:
            :class:`filestack.Filelink`: new Filelink object
        """
        sec = security or self.security
        upload_response = upload_external_url(url, self.apikey, self.storage, store_params, security=sec)
        return filestack.models.Filelink(
            handle=upload_response['handle'],
            apikey=self.apikey,
            security=sec,
            upload_response=upload_response
        )

    def upload(self, *, filepath=None, file_obj=None, store_params=None, intelligent=False, security=None):
        """
        Uploads local file or file-like object.

        Args:
            filepath (str): path to file
            file_obj (io.BytesIO or similar): file-like object
            store_params (dict): store parameters to be used during upload
            intelligent (bool): upload file using `Filestack Intelligent Ingestion
                <https://www.filestack.com/products/file-upload/technology/>`_.
            security (:class:`filestack.Security`): Security object that will be used for this API call

        Returns:
            :class:`filestack.Filelink`: new Filelink object

        Note:
            This method accepts keyword arguments only.
            Out of filepath and file_obj only one should be provided.
        """
        if store_params:  # Check the structure of parameters
            STORE_SCHEMA.check(store_params)

        upload_method = multipart_upload
        if intelligent:
            upload_method = intelligent_ingestion.upload

        response_json = upload_method(
            self.apikey, filepath, file_obj, self.storage, params=store_params, security=security or self.security
        )

        handle = response_json['handle']
        return filestack.models.Filelink(
            handle,
            apikey=self.apikey,
            security=self.security,
            upload_response=response_json
        )
```

### Summary of Changes
- Replaced `requests.get` with `FuturesSession.get` in the `zip` method.
- Used `.result()` to retrieve the response synchronously, preserving the original behavior.
- Introduced a `FuturesSession` object in the `__init__` method for handling requests.