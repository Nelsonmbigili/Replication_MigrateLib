from dataclasses import dataclass

from unidiff.patch import Hunk

from libmig.code_analysis.cg_builder import build_from_profile
from libmig.code_merge.skipped_code_detector import SkippedCodeDetector
from libmig.code_merge.skipped_code_merger import SkippedCodeMerger
from libmig.mig.mig_report_models import RoundName
from libmig.project import Project


@dataclass
class MergeInfo:
    filepath: str
    old_code: str
    new_code: str
    hunks_to_merge: list[Hunk]


class SkippedCodeMergeWorkflow:
    def __init__(self, project: Project):
        self.project = project
        self.base_round_name: RoundName = "llmmig"
        self._hunks_to_merge: list[MergeInfo] = []
        self.mig_files = None

    @property
    def _cg(self):
        if not hasattr(self, "_cg_instance"):
            self._cg_instance = build_from_profile(self.project, "premig")
        return self._cg_instance

    @property
    def _report(self):
        if not hasattr(self, "_report_instance"):
            self._report_instance = self.project.get_report()
        return self._report_instance

    def find_mig_locations(self):
        base_round_file_paths = self.project.round_paths(self.base_round_name).mig_code_files
        base_round_paths = self.project.round_paths(self.base_round_name)

        for file_path in base_round_file_paths:
            premig_code = self.project.premig_paths.read_code_file(file_path)
            base_round_code = base_round_paths.read_code_file(file_path)
            detector = SkippedCodeDetector(premig_code, base_round_code, self._cg)
            diffs_to_merge = detector.detect()
            if diffs_to_merge:
                self._hunks_to_merge.append(MergeInfo(file_path, premig_code, base_round_code, diffs_to_merge))

        self.mig_files = [merge_info.filepath for merge_info in self._hunks_to_merge]

        return self.mig_files

    def run(self):
        for merge_info in self._hunks_to_merge:
            self._merge_file(merge_info)

    def _merge_file(self, merge_info: MergeInfo):
        merger = SkippedCodeMerger(merge_info.old_code, merge_info.new_code, merge_info.hunks_to_merge)
        merged_code = merger.merge()
        self.project.merge_paths.write_code_file(merge_info.filepath, merged_code)
