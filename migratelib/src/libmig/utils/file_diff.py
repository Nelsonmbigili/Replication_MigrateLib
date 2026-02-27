import difflib

from unidiff.patch import PatchSet, PatchedFile


def compute_diff(content1: str, content2: str) -> PatchedFile | None:
    diff_lines = difflib.unified_diff(content1.splitlines(), content2.splitlines(), fromfile="a.py", tofile="b,py",
                                      lineterm='', n=0)
    patch = PatchSet(diff_lines)
    if not patch:
        return PatchedFile()

    if len(patch) > 1:
        raise ValueError("more than one files in the diff")

    hunks = patch[0]
    return hunks
