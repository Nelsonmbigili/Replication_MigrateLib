### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. **Import Replacement**: Replaced `import requests` with `import httpx`.
2. **SSL Warning Handling**: `httpx` does not use `urllib3` directly, so the `InsecureRequestWarning` from `urllib3` was replaced with `httpx`'s `InsecureRequestWarning`.
3. **HTTP GET Request**: Replaced `requests.get` with `httpx.get`. The `stream=True` and `verify=False` arguments are still supported in `httpx`.
4. **Streaming Content**: Replaced `req.iter_content(chunk_size=1024)` with `req.iter_bytes(chunk_size=1024)`, as `httpx` uses `iter_bytes` for streaming content.
5. **Headers Access**: Accessing headers remains the same (`req.headers`).
6. **Error Handling**: `httpx` raises exceptions for HTTP errors by default, so `req.raise_for_status()` remains unchanged.

### Modified Code
Here is the updated code using `httpx` version 0.28.1:

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
def http_get_temp(url: str, temp_file: IO) -> None:
    import httpx
    import warnings
    from httpx import InsecureRequestWarning

    # temporary fix for dealing with this SSL certificate issue:
    # https://github.com/bheinzerling/bpemb/issues/63
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InsecureRequestWarning)
        req = httpx.get(url, stream=True, verify=False)

    req.raise_for_status()
    content_length = req.headers.get('Content-Length')
    total = int(content_length) if content_length is not None else None
    try:
        from tqdm import tqdm
        progress = tqdm(unit="B", total=total)
    except ImportError:
        progress = None
    for chunk in req.iter_bytes(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            if progress is not None:
                progress.update(len(chunk))
            temp_file.write(chunk)
    if progress is not None:
        progress.close()
    return req.headers


# source: https://github.com/allenai/allennlp/blob/master/allennlp/common/file_utils.py#L147  # NOQA
def http_get(url: str, outfile: Path, ignore_tardir=False) -> None:
    import tempfile
    import shutil
    with tempfile.NamedTemporaryFile() as temp_file:
        headers = http_get_temp(url, temp_file)
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

### Summary of Changes
- Replaced `requests` with `httpx` for HTTP requests.
- Updated streaming content handling to use `iter_bytes` instead of `iter_content`.
- Adjusted SSL warning handling to use `httpx`'s `InsecureRequestWarning`.