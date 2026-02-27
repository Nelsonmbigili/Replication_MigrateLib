### Explanation of Changes:
To migrate from `tqdm` to `alive-progress`, the following changes were made:
1. **Import Replacement**: Removed the import of `tqdm` and replaced it with `alive-progress`.
2. **Progress Bar Initialization**: Replaced `tqdm.pandas()` with `alive-progress`'s equivalent functionality using `alive_bar`.
3. **Progress Application**: Replaced `progress_apply` calls with a manual iteration using `alive_bar` to track progress.
4. **Custom Progress Handling**: Since `alive-progress` does not directly integrate with pandas like `tqdm.pandas()`, loops were added to manually iterate over the data and apply transformations while updating the progress bar.

### Modified Code:
```python
#!/usr/bin/env python3

## Main functions of the preprocessing API
# Copyright (C) <2018-2022>  <Agence Data Services, DSI Pôle Emploi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Functions:
# - notnull -> Replaces null values by an empty character
# - remove_non_string -> Replaces all non strings by an empty character
# - get_true_spaces -> Replaces all whitespaces by a single space
# - to_lower -> Transforms the string to lower case
# - pe_matching -> Specific one-to-one tokens replacements
# - remove_punct -> Replaces all non alpha-numeric characters by spaces
# - trim_string -> Trims spaces at the beginning and ending of the string (multiple spaces become one)
# - remove_numeric -> Replaces numeric strings by a space
# - remove_stopwords -> Removes stopwords
# - remove_accents -> Removes all accents and special characters (ç..)
# - remove_gender_synonyms -> [French] Removes gendered synonyms
# - lemmatize -> Lemmatizes the document
# - stemmatize -> Stemmatizes the words of the document
# - add_point -> Adds a dot at the end of each line
# - deal_with_specific_characters -> Adds spaces before and after some punctuations (, : ; .)
# - replace_urls -> Replaces URLs by spaces
# - remove_words -> Replaces words from a list
# - fix_text -> Fixes numerous inconsistencies within a text (via ftfy)

import ftfy
import logging
import unicodedata
import numpy as np
import pandas as pd
from typing import List, Union
from nltk.stem.snowball import FrenchStemmer

from alive_progress import alive_bar  # Replaced tqdm with alive-progress
from words_n_fun import utils
from words_n_fun.preprocessing import (lemmatizer, stopwords,
                                       synonym_malefemale_replacement)

# Get logger
logger = logging.getLogger(__name__)


def impl_remove_non_string(docs: pd.Series, use_tqdm: bool = False) -> pd.Series:
    '''Replaces all non strings by an empty character

    Args:
        docs (pd.Series): Documents to process

    Returns:
        pd.Series: Modified documents
    '''
    if use_tqdm:
        with alive_bar(len(docs), title="Processing non-strings") as bar:
            return pd.Series([x if isinstance(x, str) else '' for x in docs.apply(lambda x: bar() or x)])
    else:
        return docs.apply(lambda x: x if isinstance(x, str) else '')


@utils.data_agnostic
def remove_non_string(docs: pd.Series, use_tqdm: bool = False) -> pd.Series:
    return impl_remove_non_string(docs, use_tqdm)


@utils.regroup_data_series
def impl_to_lower(docs: pd.Series, threshold_nb_chars: int = 0, use_tqdm: bool = False) -> pd.Series:
    '''Transforms the string to lower case

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        threshold_nb_chars (int): Minimum number of characters for a token to be transformed to lowercase (def=0).

    Returns:
        pd.Series: Modified documents
    '''
    if threshold_nb_chars > 1:
        logger.debug(f"Applying lower case transform for tokens of at least {threshold_nb_chars} chars.")
        if use_tqdm:
            with alive_bar(len(docs), title="Converting to lowercase") as bar:
                return pd.Series([
                    " ".join(x.lower() if len(x) >= threshold_nb_chars else x for x in x.split(" "))
                    if isinstance(x, str) else None
                    for x in docs.apply(lambda x: bar() or x)
                ])
        else:
            return docs.apply(lambda x: " ".join(x.lower() if len(x) >= threshold_nb_chars else x for x in x.split(" ")) if isinstance(x, str) else None)
    else:
        return docs.str.lower()


@utils.data_agnostic
def to_lower(docs: pd.Series, threshold_nb_chars: int = 0, use_tqdm: bool = False) -> pd.Series:
    '''Transforms the string to lower case

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        threshold_nb_chars (int): Minimum number of characters for a token to be transformed to lowercase (def=0).

    Returns:
        pd.Series: Modified documents
    '''
    logger.debug('Calling basic.to_lower')
    return impl_to_lower(docs, threshold_nb_chars, use_tqdm)


@utils.regroup_data_series
def impl_remove_accents(docs: pd.Series, use_tqdm: bool = False) -> pd.Series:
    '''Removes all accents and special characters (ç..)

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        use_tqdm (bool): Whether tqdm should be used (default: True)

    Returns:
        pd.Series: Modified documents
    '''
    if use_tqdm:
        with alive_bar(len(docs), title="Removing accents") as bar:
            return pd.Series([
                ''.join((c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn'))
                if isinstance(x, str) else None
                for x in docs.apply(lambda x: bar() or x)
            ])
    else:
        return docs.apply(lambda x: ''.join((c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn')) if isinstance(x, str) else None)


@utils.data_agnostic
def remove_accents(docs: pd.Series, use_tqdm: bool = False) -> pd.Series:
    '''Removes all accents and special characters (ç..)

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        use_tqdm (bool): Whether tqdm should be used (default: True)

    Returns:
        pd.Series: Modified documents
    '''
    return impl_remove_accents(docs, use_tqdm)


@utils.regroup_data_series
def impl_fix_text(docs: pd.Series, use_tqdm: bool = False, **ftfy_kwargs) -> pd.Series:
    '''Fixes numerous inconsistencies within a text (via ftfy)

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        ftfy_kwargs (dict): Kwargs forwarded to ftfy

    Returns:
        pd.Series: Modified documents
    '''
    if use_tqdm:
        with alive_bar(len(docs), title="Fixing text") as bar:
            return pd.Series([
                ftfy.fix_text(x, **ftfy_kwargs) if isinstance(x, str) else None
                for x in docs.apply(lambda x: bar() or x)
            ])
    else:
        return docs.apply(lambda x: ftfy.fix_text(x, **ftfy_kwargs) if isinstance(x, str) else None)


@utils.data_agnostic
def fix_text(docs: pd.Series, use_tqdm: bool = False, **ftfy_kwargs) -> pd.Series:
    '''Fixes numerous inconsistencies within a text (via ftfy)

    Args:
        docs (pd.Series): Documents to process
    Kwargs:
        ftfy_kwargs (dict): Kwargs forwarded to ftfy

    Returns:
        pd.Series: Modified documents
    '''
    logger.debug('Calling basic.fix_text')
    return impl_fix_text(docs, use_tqdm, **ftfy_kwargs)


if __name__ == '__main__':
    logger.error("This script is not stand alone but belongs to a package that has to be imported.")
```

### Key Notes:
- The `alive_bar` is used to manually iterate over the data and update the progress bar.
- The `use_tqdm` flag is retained for compatibility but now uses `alive-progress` when enabled.
- The changes are limited to replacing `tqdm` functionality with `alive-progress` while maintaining the original structure and logic.