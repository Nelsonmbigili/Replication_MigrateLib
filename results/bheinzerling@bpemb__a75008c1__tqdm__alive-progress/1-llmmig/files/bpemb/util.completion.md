### Explanation of Changes:
To migrate the code from using the `tqdm` library to the `alive-progress` library, the following changes were made:
1. Replaced the import statement for `tqdm` with `alive-progress`.
2. Used the `alive_bar` context manager from `alive-progress` to create a progress bar.
3. Since `alive-progress` does not directly support byte-based progress tracking, the `total` parameter was converted to represent the number of chunks (calculated as `total // chunk_size`).
4. Updated the progress bar to increment by 1 for each chunk processed, as `alive-progress` tracks progress in terms of iterations rather than bytes.

### Modified Code:
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
    import requests
    import warnings
    from urllib3.exceptions import InsecureRequestWarning
    from alive_progress import alive_bar

    # temporary fix for dealing with this SSL certificate issue:
    # https://github.com/bheinzerling/bpemb/issues/63
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InsecureRequestWarning)
        req = requests.get(url, stream=True, verify=False)

    req.raise_for_status()
    content_length = req.headers.get('Content-Length')
    total = int(content_length) if content_length is not None else None
    chunk_size = 1024
    num_chunks = (total // chunk_size) + 1 if total is not None else None

    with alive_bar(num_chunks, title="Downloading", bar="blocks", spinner="dots") as progress:
        for chunk in req.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                progress()  # Increment the progress bar by 1 chunk
                temp_file.write(chunk)
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

### Key Points:
- The `alive_bar` context manager is used to create a progress bar.
- The `total` parameter for `alive_bar` is calculated as the number of chunks (`total // chunk_size`).
- The `progress()` method is called once for each chunk processed to update the progress bar.
- The `alive-progress` library provides a more visually appealing progress bar with customizable styles.