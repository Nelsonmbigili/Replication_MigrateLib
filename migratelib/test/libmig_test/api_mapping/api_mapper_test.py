from pathlib import Path

import pytest

from libmig.api_mapping.api_mapper import APIMapper, api_description
from libmig.lib_index.api_models import API
from libmig.lib_index.lib_index import LibIndex
from libmig.utils.venv import get_venv


@pytest.fixture
def venv():
    venv_path = Path(__file__).parent / ".venv"
    v = get_venv(venv_path, "3.12")
    v.create()
    v.install("requests", "2.32.3")
    v.install("httpx", "0.28.1")
    (venv_path / ".gitignore").write_text("*")
    return v


@pytest.fixture
def lib_index_cache_dir():
    index_dir = Path(__file__).parent / ".libindex"
    index_dir.mkdir(exist_ok=True)
    (index_dir / ".gitignore").write_text("*")
    return index_dir


def test_one_to_one_mapping(venv, lib_index_cache_dir):
    src_lib = LibIndex.from_venv("requests", venv)
    tgt_lib = LibIndex.from_venv("httpx", venv)

    mapper = APIMapper(src_lib, tgt_lib)
    src_api = src_lib.search_apis("get")[0]
    tgt_api, similarity = mapper.map(src_api)[0]

    assert tgt_api.short_name == "get"


def check_similarity(src_qname: str, src_sign: str, src_doc: str, tgt_qname: str, tgt_sign: str, tgt_doc: str,
                     min_similarity: float, max_similarity: float):
    src_api = API(src_qname, src_qname.split(".")[-1], src_sign, "xxx", "xxx.py", 1, src_doc)
    tgt_api = API(tgt_qname, tgt_qname.split(".")[-1], tgt_sign, "xxx", "xxx.py", 1, tgt_doc)

    from sentence_transformers import SentenceTransformer, util
    _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    src_desc = api_description(src_api)
    src_emb = _embedder.encode(src_desc)
    tgt_desc = api_description(tgt_api)
    tgt_emb = _embedder.encode(tgt_desc)
    similarity = util.pytorch_cos_sim(src_emb, tgt_emb).item()
    print(f"Similarity between {src_qname} and {tgt_qname}: {similarity}")
    assert min_similarity <= similarity <= max_similarity


def test_similarity():
    check_similarity("Parameter",
                     "(param_decls: Optional[Sequence[str]] = None, type: Union[click.types.ParamType, Any, NoneType] = None, required: bool = False, default: Union[Any, Callable[[], Any], NoneType] = None, callback: Optional[Callable[[click.core.Context, ForwardRef('Parameter'), Any], Any]] = None, nargs: Optional[int] = None, multiple: bool = False, metavar: Optional[str] = None, expose_value: bool = True, is_eager: bool = False, envvar: Union[Sequence[str], str, NoneType] = None, shell_complete: Optional[Callable[[click.core.Context, ForwardRef('Parameter'), str], Union[List[ForwardRef('CompletionItem')], List[str]]]] = None) -> None",
                     """A parameter to a command comes in two versions: they are either
           :class:`Option`\s or :class:`Argument`\s.  Other subclasses are currently
           not supported by design as some of the internals for parsing are
           intentionally not finalized.
           
           Some settings are supported by both options and arguments.
           
           :param param_decls: the parameter declarations for this option or
                               argument.  This is a list of flags or argument
                               names.
           :param type: the type that should be used.  Either a :class:`ParamType`
                        or a Python type.  The latter is converted into the former
                        automatically if supported.
           :param required: controls if this is optional or not.
           :param default: the default value if omitted.  This can also be a callable,
                           in which case it's invoked when the default is needed
                           without any arguments.
           :param callback: A function to further process or validate the value
               after type conversion. It is called as ``f(ctx, param, value)``
               and must return the value. It is called for all sources,
               including prompts.
           :param nargs: the number of arguments to match.  If not ``1`` the return
                         value is a tuple instead of single value.  The default for
                         nargs is ``1`` (except if the type is a tuple, then it's
                         the arity of the tuple). If ``nargs=-1``, all remaining
                         parameters are collected.
           :param metavar: how the value is represented in the help page.
           :param expose_value: if this is `True` then the value is passed onwards
                                to the command callback and stored on the context,
                                otherwise it's skipped.
           :param is_eager: eager values are processed before non eager ones.  This
                            should not be set for arguments or it will inverse the
                            order of processing.
           :param envvar: a string or list of strings that are environment variables
                          that should be checked.
           :param shell_complete: A function that returns custom shell
               completions. Used instead of the param's type completion if
               given. Takes ``ctx, param, incomplete`` and must return a list
               of :class:`~click.shell_completion.CompletionItem` or a list of
               strings.
           
           .. versionchanged:: 8.0
               ``process_value`` validates required parameters and bounded
               ``nargs``, and invokes the parameter callback before returning
               the value. This allows the callback to validate prompts.
               ``full_process_value`` is removed.
           
           .. versionchanged:: 8.0
               ``autocompletion`` is renamed to ``shell_complete`` and has new
               semantics described above. The old name is deprecated and will
               be removed in 8.1, until then it will be wrapped to match the
               new requirements.
           
           .. versionchanged:: 8.0
               For ``multiple=True, nargs>1``, the default must be a list of
               tuples.
           
           .. versionchanged:: 8.0
               Setting a default is no longer required for ``nargs>1``, it will
               default to ``None``. ``multiple=True`` or ``nargs=-1`` will
               default to ``()``.
           
           .. versionchanged:: 7.1
               Empty environment variables are ignored rather than taking the
               empty string value. This makes it possible for scripts to clear
               variables if they can't unset them.
           
           .. versionchanged:: 2.0
               Changed signature for parameter callback to also be passed the
               parameter. The old callback format will still work, but it will
               raise a warning to give you a chance to migrate the code easier.""",
                     "CallbackParam",
                     "(param_decls: Optional[Sequence[str]] = None, type: Union[click.types.ParamType, Any, NoneType] = None, required: bool = False, default: Union[Any, Callable[[], Any], NoneType] = None, callback: Optional[Callable[[click.core.Context, ForwardRef('Parameter'), Any], Any]] = None, nargs: Optional[int] = None, multiple: bool = False, metavar: Optional[str] = None, expose_value: bool = True, is_eager: bool = False, envvar: Union[Sequence[str], str, NoneType] = None, shell_complete: Optional[Callable[[click.core.Context, ForwardRef('Parameter'), str], Union[List[ForwardRef('CompletionItem')], List[str]]]] = None) -> None",
                     "", 0.9, 1.0)

    check_similarity("detect_all",
                     "(byte_str: Union[bytes, bytearray], ignore_threshold: bool = False, should_rename_legacy: bool = False) -> List[dict]", """"Detect all the possible encodings of the given byte string.

:param byte_str:          The byte sequence to examine.
:type byte_str:           ``bytes`` or ``bytearray``
:param ignore_threshold:  Include encodings that are below
                          ``UniversalDetector.MINIMUM_THRESHOLD``
                          in results.
:type ignore_threshold:   ``bool``
:param should_rename_legacy:  Should we rename legacy encodings
                              to their more modern equivalents?
:type should_rename_legacy:   ``bool``""", "detect",
                     "(byte_str: 'bytes', should_rename_legacy: 'bool' = False, **kwargs: 'Any') -> 'ResultDict'", """chardet legacy method
Detect the encoding of the given byte string. It should be mostly backward-compatible.
Encoding name will match Chardet own writing whenever possible. (Not on encoding name unsupported by it)
This function is deprecated and should be used to migrate your project easily, consult the documentation for
further information. Not planned for removal.

:param byte_str:     The byte sequence to examine.
:param should_rename_legacy:  Should we rename legacy encodings
                              to their more modern equivalents?""", 0.8, .9)
