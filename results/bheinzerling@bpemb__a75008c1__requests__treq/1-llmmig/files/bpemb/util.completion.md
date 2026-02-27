### Explanation of Changes
The migration from `requests` to `treq` involves the following changes:
1. **Import Changes**: Replace the `requests` import with `treq`.
2. **Asynchronous Nature of `treq`**: `treq` is built on `Twisted` and is asynchronous. Therefore, the `http_get_temp` function must be converted to an asynchronous function using `async def`.
3. **Request Execution**: Replace `requests.get` with `treq.get`. The `treq.get` method returns a `Deferred` object, which we await to get the response.
4. **Reading Response Content**: Replace `req.iter_content` with `response.iter_content` (from `treq`), which is an asynchronous generator.
5. **Progress Bar Updates**: Update the progress bar in an asynchronous loop while reading chunks of data.
6. **Headers Access**: Access headers using `response.headers` in `treq`.

### Modified Code
Below is the modified code after migrating to `treq`:

```python
from pathlib import Path
from typing import IO


def sentencepiece_load(file):
    """Load a SentencePiece model"""
    from sentencepiece import SentencePieceProcessor
    spm = SentencePieceProcessor()
    spm.Load(str(file))
    return spm


# source: https://github.com/allenai/allennlp/blob/master/allennlp/common/file_utils.py#L147  # NOQA
async def http_get_temp(url: str, temp_file: IO) -> None:
    import treq
    import warnings
    from twisted.internet.defer import ensureDeferred
    from urllib3.exceptions import InsecureRequestWarning

    # temporary fix for dealing with this SSL certificate issue:
    # https://github.com/bheinzerling/bpemb/issues/63
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InsecureRequestWarning)
        response = await treq.get(url, unbuffered=True, verify=False)

    if response.code != 200:
        response.raise_for_status()

    content_length = response.headers.get(b'Content-Length')
    total = int(content_length) if content_length is not None else None
    try:
        from tqdm import tqdm
        progress = tqdm(unit="B", total=total)
    except ImportError:
        progress = None

    async for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            if progress is not None:
                progress.update(len(chunk))
            temp_file.write(chunk)

    if progress is not None:
        progress.close()
    return response.headers


# source: https://github.com/allenai/allennlp/blob/master/allennlp/common/file_utils.py#L147  # NOQA
async def http_get(url: str, outfile: Path, ignore_tardir=False) -> None:
    import tempfile
    import shutil
    with tempfile.NamedTemporaryFile() as temp_file:
        headers = await http_get_temp(url, temp_file)
        # we are copying the file before closing it, flush to avoid truncation
        temp_file.flush()
        # shutil.copyfileobj() starts at current position, so go to the start
        temp_file.seek(0)
        outfile.parent.mkdir(exist_ok=True, parents=True)
        content_header = headers.get(b"Content-Type")
        if content_header and b"gzip" in content_header:
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

### Key Notes:
1. The `http_get_temp` and `http_get` functions are now asynchronous (`async def`).
2. The `treq.get` method is used to make HTTP requests, and its response is awaited.
3. The `response.iter_content` method is used to read the response in chunks asynchronously.
4. Headers are accessed as byte strings (e.g., `b'Content-Length'`).
5. The rest of the code remains unchanged to ensure compatibility with the larger application.