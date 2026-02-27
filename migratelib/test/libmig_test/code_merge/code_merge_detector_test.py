from libmig.code_merge.skipped_code_detector import detect_code_skipping_comment
from libmig_test.completion_resources import completion_1


def test_is_merge_required(completion_1: str):
    similarity, matching_phrase = detect_code_skipping_comment(completion_1)
    print(similarity, matching_phrase)
    assert bool(matching_phrase)


def test_x():
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
    from libmig.utils.file_diff import compute_diff
    patch = compute_diff(before, after)
    hunk1, hunk2, hunk3 = patch
    assert hunk1.removed == 3
    assert hunk2.removed == 1

    assert hunk1.target_start == 1
    assert hunk2.target_start == 3
    print(patch)
