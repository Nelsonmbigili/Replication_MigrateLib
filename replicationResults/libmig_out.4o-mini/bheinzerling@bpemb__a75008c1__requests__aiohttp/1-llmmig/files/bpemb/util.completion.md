### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is an asynchronous HTTP client.
2. **Asynchronous Functions**: The `http_get_temp` function was modified to be asynchronous (`async def`) and uses `await` for making the HTTP GET request.
3. **Session Management**: An `aiohttp.ClientSession` was created to manage the connection pool and make requests. This is necessary for `aiohttp` to function properly.
4. **Reading Response**: The response content is read asynchronously using `await response.content.read()`, and the chunks are processed in a loop using `await response.content.iter_any()`.
5. **Error Handling**: The error handling for HTTP status codes remains similar, but it uses `raise_for_status()` on the response object.
6. **Temporary File Handling**: The temporary file handling remains the same, but it is now done in an asynchronous context.

Here is the modified code:

```python
from pathlib import Path
from typing import IO
import aiohttp
import asyncio
import warnings
from urllib3.exceptions import InsecureRequestWarning


def sentencepiece_load(file):
    """Load a SentencePiece model"""
    from sentencepiece import SentencePieceProcessor
    spm = SentencePieceProcessor()
    spm.Load(str(file))
    return spm


async def http_get_temp(url: str, temp_file: IO) -> None:
    # temporary fix for dealing with this SSL certificate issue:
    # https://github.com/bheinzerling/bpemb/issues/63
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InsecureRequestWarning)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                content_length = response.headers.get('Content-Length')
                total = int(content_length) if content_length is not None else None
                try:
                    from tqdm import tqdm
                    progress = tqdm(unit="B", total=total)
                except ImportError:
                    progress = None
                async for chunk in response.content.iter_any(1024):
                    if chunk:  # filter out keep-alive new chunks
                        if progress is not None:
                            progress.update(len(chunk))
                        temp_file.write(chunk)
                if progress is not None:
                    progress.close()
    return response.headers


async def http_get(url: str, outfile: Path, ignore_tardir=False) -> None:
    import tempfile
    import shutil
    async with tempfile.NamedTemporaryFile() as temp_file:
        headers = await http_get_temp(url, temp_file)
        # we are copying the file before closing it, flush to avoid truncation
        temp_file.flush()
        # shutil.copyfileobj() starts at current position, so go to the start
        temp_file.seek(0)
        outfile.parent.mkdir(exist_ok=True, parents=True)
        content_header = headers.get("Content-Type")
        if content_header and "gzip" in content_header:
            import tarfile
            tf = tarfile.open(fileobj=temp_file)
            members = tf.getmembers()
            if len(members) != 1:
                raise NotImplementedError("TODO: extract multiple files")
            member = members[0]
            if ignore_tardir:
                member.name = Path(member.name).name
            tf.extract(member, str(outfile.parent))
            extracted_file = outfile.parent / member.name
            assert extracted_file == outfile, "{} != {}".format(
                extracted_file, outfile)
        else:
            with open(str(outfile), 'wb') as out:
                shutil.copyfileobj(temp_file, out)
    return outfile


def load_word2vec_file(word2vec_file, add_pad=False, pad="<pad>"):
    """Load a word2vec file in either text or bin format."""
    from gensim.models import KeyedVectors
    word2vec_file = str(word2vec_file)
    binary = word2vec_file.endswith(".bin")
    vecs = KeyedVectors.load_word2vec_format(word2vec_file, binary=binary)
    if add_pad:
        if pad not in vecs:
            add_embeddings(vecs, pad)
        else:
            raise ValueError("Attempted to add <pad>, but already present")
    return vecs


def add_embeddings(keyed_vectors, *words, init=None):
    import numpy as np
    if init is None:
        init = np.zeros
    vectors_to_add = init((len(words), keyed_vectors.vectors.shape[1]))
    keyed_vectors.add_vectors(words, vectors_to_add)
    return keyed_vectors.vectors.shape[0]
```

### Note
To run the asynchronous functions, you will need to use an event loop, such as `asyncio.run(http_get(url, outfile))`, in the main part of your application.