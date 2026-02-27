### Explanation of Changes:
To migrate from `tqdm` to `progressbar2`, the following changes were made:
1. Replaced the `tqdm` import with `progressbar` (from `progressbar2`).
2. Replaced the `tqdm` progress bar initialization with `progressbar.ProgressBar`.
3. Updated the progress bar's `update` method to use `progressbar`'s `update` method, which requires the current progress value instead of the increment.
4. Added logic to track the cumulative progress manually, as `progressbar` does not handle incremental updates directly like `tqdm`.

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

    # temporary fix for dealing with this SSL certificate issue:
    # https://github.com/bheinzerling/bpemb/issues/63
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InsecureRequestWarning)
        req = requests.get(url, stream=True, verify=False)

    req.raise_for_status()
    content_length = req.headers.get('Content-Length')
    total = int(content_length) if content_length is not None else None
    try:
        import progressbar
        progress = progressbar.ProgressBar(max_value=total, widgets=[
            progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ',
            progressbar.FileTransferSpeed(), ' ',
            progressbar.ETA()
        ])
    except ImportError:
        progress = None

    downloaded = 0  # Track cumulative progress
    for chunk in req.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            if progress is not None:
                downloaded += len(chunk)
                progress.update(downloaded)
            temp_file.write(chunk)
    if progress is not None:
        progress.finish()
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
- The `progressbar.ProgressBar` requires the total value (`max_value`) and updates with the cumulative progress, unlike `tqdm`, which updates incrementally.
- A `downloaded` variable was introduced to track the cumulative progress for `progressbar`.
- The `progress.finish()` method is called at the end to ensure the progress bar is properly finalized.