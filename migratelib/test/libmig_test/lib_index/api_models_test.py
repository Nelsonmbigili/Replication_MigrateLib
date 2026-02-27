from libmig.lib_index.api_models import API


def test__is_public():
    api = API(qualified_name="a.b.c", short_name="c", signature="def c():", type="function", file="a.py", line=1,
              doc="doc")
    assert api.is_public() is True

    api = API(qualified_name="a.b._c", short_name="_c", signature="def _c():", type="function", file="a.py", line=1,
              doc="doc")
    assert api.is_public() is False

    api = API(qualified_name="a._b.c", short_name="c", signature="def _c():", type="function", file="a.py", line=1,
              doc="doc")
    assert api.is_public() is False

    api = API(qualified_name="a._b._c", short_name="_c", signature="def _c():", type="function", file="a.py", line=1,
              doc="doc")
    assert api.is_public() is False

    api = API(qualified_name="_c", short_name="_c", signature="def _c():", type="function", file="a.py", line=1,
              doc="doc")

    assert api.is_public() is False
