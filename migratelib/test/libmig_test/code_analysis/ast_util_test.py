from libmig.code_analysis.ast_util import find_asynced_defs


def test_find_asynced_defs__single_match():
    code_before = """
def sync_before_sync_after(a, b):
    pass

def sync_before_async_after(x, y):
    pass
    
async def async_before_sync_after(m):
    pass
    
async def async_before_async_after(n):
    pass
"""
    code_after = """
def sync_before_sync_after(a, b):
    pass
    
async def sync_before_async_after(x, y):
    pass
    
def async_before_sync_after(m):
    pass
    
async def async_before_async_after(n):
    pass
"""

    actual = {after.name for before, after in find_asynced_defs(code_before, code_after)}
    expected = {"sync_before_async_after"}
    assert actual == expected


def test_find_asynced_defs__multiple_matches__diff_args():
    code_before = """
class A:
    def foo(x, y):
        pass
        
class B:
    def foo(p):
        pass
"""
    code_after = """
class A:
    async def foo(a, b):
        pass
        
class B:
    def foo(p):
        pass
"""

    actual = find_asynced_defs(code_before, code_after)
    assert len(actual) == 1

    before, after = actual[0]
    assert after.name == "foo"
    assert len(after.args.args) == 2


def test_multiple_after_matches_to_one_before():
    code_before = """
class A: 
    def foo(x): # line 3
        pass

class B:
    def foo(y): # line 7
        pass
"""
    code_after = """
class A: 
    async def foo(a): # line 3
        pass

class B: 
    async def foo(b): # line 7
        pass
"""

    actuals = find_asynced_defs(code_before, code_after)
    assert len(actuals) == 2
    line_3_after, line_3_before = [(after, before) for after, before in actuals if after.lineno == 3][0]
    line_7_after, line_7_before = [(after, before) for after, before in actuals if after.lineno == 7][0]

    assert line_3_after.lineno == 3
    assert line_7_before.lineno == 7
