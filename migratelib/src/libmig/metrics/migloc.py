from unidiff.patch import Hunk

from libmig.mig.mig_report_models import MigRoundReport, RoundName, MigReport
from libmig.mig.mig_round_paths import MigRoundPaths
from libmig.project import Project
from libmig.utils.file_diff import compute_diff


def file_mig_loc(code_before: str, code_after: str):
    patch = compute_diff(code_before, code_after)
    added_lines = 0
    removed_lines = 0

    hunk: Hunk
    for hunk in patch:
        added_lines += hunk.added
        removed_lines += hunk.removed
    return added_lines + removed_lines


def mig_loc(base_round_paths: MigRoundPaths, this_round_paths: MigRoundPaths = MigRoundPaths):
    """ Calculate the Migration LOC from a base round to a specific round.
    :param base_round_paths: file paths to the base round.
    :param this_round_paths: The round to calculate the LOC for. If None, uses the best round.
    :return: total number of added and removed lines to go from base_round to this_round.
    """

    total_mig_loc = 0
    for file in this_round_paths.mig_code_files:
        base_file = base_round_paths.read_code_file(file)
        this_file = this_round_paths.read_code_file(file)
        total_mig_loc += file_mig_loc(base_file, this_file)

    return total_mig_loc
