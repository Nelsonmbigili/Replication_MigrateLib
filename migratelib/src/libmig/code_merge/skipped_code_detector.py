import re

from unidiff.patch import Hunk

from libmig.utils.cgx import CGX
from libmig.utils.file_diff import compute_diff


# Findings:
# - size difference is a better estimate of code skipping than the code skipping comment
# -   Actually instead of a plain sze difference, removed hunk size difference would be even better
# - The removed hunks should be few large hunks rather than many small hunks
# - after merge, verify by parsing the code, and then run tests

# Proposed heuristic:
# - calculate relative removed size = removed_lines / (removed_lines + added_lines)
# - if absolute removed line is above threashold (10 lines), and relative removed size is above threshold (0.7), then needs marging
# removed code has no source API usage (so it should not be removed)

class SkippedCodeDetector:
    def __init__(self, code_before: str, code_after: str, cg_before: CGX):
        self.code_before = code_before
        self.code_after = code_after
        self.cg_before = cg_before

    def detect(self) -> list[Hunk]:
        patch = compute_diff(self.code_before, self.code_after)
        total = patch.removed + patch.added
        remove_ratio = (patch.removed / total) if total > 0 else -1

        if patch.removed < 10 and remove_ratio < 0.7:
            # unlikely to have code skipping
            return []

        removed_hunks = []
        for hunk in patch:
            if hunk.removed < 10:
                continue
            if hunk.removed < 20:
                # if hunk is still small (20 or less line) and has API use, may be migration related
                if hunk.added > 0:
                    continue
                removed_line_numbers = {line.source_line_no for line in hunk.target_lines()}
                has_api_use = any(call for call in self.cg_before.direct_calls if call.call_line in removed_line_numbers)
                if has_api_use:
                    continue
            else:
                # if big hunk, we look at ratio
                ratio = hunk.removed / (hunk.removed + hunk.added)
                if ratio < 0.9:
                    continue

            removed_hunks.append(hunk)

        return removed_hunks


def detect_code_skipping_comment(completion: str):
    threshold = .8
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # split the completion into segments, by new lines or sentence endings

    completion_parts = re.split(r'\n\s*\n|(?<=[.!?])\s+', completion)

    target_phrase = "rest of the code remains unchanged"
    target_embedding = model.encode(target_phrase, convert_to_tensor=True)

    best_match = ""
    best_similarity = -1
    for part in completion_parts:
        completion_embedding = model.encode(part, convert_to_tensor=True)
        similarity = util.cos_sim(target_embedding, completion_embedding).item()
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = part

        if best_similarity > threshold:
            break

    return best_similarity, best_match
