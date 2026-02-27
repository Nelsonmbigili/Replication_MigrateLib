from libmig.code_merge.skipped_code_merger import SkippedCodeMerger
from libmig.utils.file_diff import compute_diff


def test_code_merging():
    before = """
a
b
c
d
e
f
g
h
i
j
        """.strip()

    after = """
a
e
f
h
x
j
    """.strip()

    hunk1, hunk2, hunk3 = compute_diff(before, after)
    merger = SkippedCodeMerger(before, after, [hunk1])
    merged = merger.merge()
    assert merged == """
a
b
c
d
e
f
h
x
j
    """.strip()
