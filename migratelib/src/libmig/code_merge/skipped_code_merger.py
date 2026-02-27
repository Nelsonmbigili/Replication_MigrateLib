from unidiff.patch import Hunk


class SkippedCodeMerger:
    def __init__(self, old_code: str, new_code: str, hunks_to_merge: list[Hunk]):
        self.old_code = old_code
        self.new_code = new_code
        self.hunks_to_merge = hunks_to_merge

    def merge(self) -> str:
        sorted_hunks = sorted(self.hunks_to_merge, key=lambda h: h.target_start, reverse=True)
        merged_lines = self.new_code.splitlines(keepends=False)
        for hunk in sorted_hunks:
            code_to_merge = [ln.value for ln in hunk.source_lines()]
            merged_lines = merged_lines[:hunk.target_start] + code_to_merge + merged_lines[hunk.target_start:]

        return "\n".join(merged_lines)
