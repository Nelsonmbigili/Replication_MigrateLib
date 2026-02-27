from libmig.code_analysis.cg_builder import build_from_profile
from libmig.mdutils import extract_code
from libmig.mig.mig_error import MigError, ErrorCode
from libmig.mig.mig_report_models import MigRoundReport
from libmig.mig_file_search.lib_usage_mig_file_finder import LibUsageMigFileFinder
from libmig.project import Project
from libmig.prompting.first_round_prompt_builder import FirstRoundPromptBuilder
from libmig.prompting.prompt_builder_base import PromptBuilderBase


class LLMMigWorkflow:
    def __init__(self, project: Project):
        self.project = project
        self.log = project.get_loger()
        self._has_new_files = False
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
        project = self.project
        cg = build_from_profile(project, "premig")
        runtime_files = {call.caller.file for call in cg.direct_calls if
                         call.caller.owner == "client" and call.callee.owner == project.source}

        import_files = LibUsageMigFileFinder(project).find()
        all_files = sorted(runtime_files.union(import_files))

        if not all_files:
            raise MigError(ErrorCode.NO_FILES_TO_MIGRATE, "no files to migrate")
        elif len(all_files) > project.max_files:
            raise MigError(ErrorCode.TOO_MANY_FILES_TO_MIGRATE, "too many files to migrate",
                           f"max files: {project.max_files}, found: {len(all_files)}")
        self.mig_files = all_files
        return all_files

    def run(self):
        if not self.mig_files:
            raise MigError(ErrorCode.NO_FILES_TO_MIGRATE, "no files to migrate")
        self.log.log_event(f"starting llmmig round", "h2")
        self.log.log_event(f"migrating {len(self.mig_files)} files", "l1")
        self.init_output()
        self._has_new_files = self.migrate_all_files()

    def migrate_all_files(self):
        prompt_builder = FirstRoundPromptBuilder(self.project)
        log = self.log
        has_new_files = False
        for file in self.mig_files:
            log.log_event(f"migrating {file}", "h3")
            from_cache = self.migrate_file(file, prompt_builder)
            if not from_cache:
                _has_new_files = True

        return has_new_files

    def migrate_file(self, file: str, prompt_builder: PromptBuilderBase):
        project = self.project

        completion_file = project.llmmig_paths.file_with_suffix(file, ".completion.md", True)

        if completion_file.exists() and project.use_cache:
            completion = completion_file.read_text("utf-8")
            from_cache = True
        else:
            llm_client = project.create_llm_client()
            prompt = prompt_builder.build(file)
            project.llmmig_paths.file_with_suffix(file, ".prompt.md", True).write_text(prompt, "utf-8")

            if project.dry_run:
                return False

            completion = llm_client.request([{"role": "user", "content": prompt}])
            completion_file.write_text(completion, "utf-8")
            from_cache = False

        postmig_code = extract_code(completion)
        project.llmmig_paths.write_code_file(file, postmig_code)

        return from_cache

    def init_output(self):
        premig_paths = self.project.premig_paths
        self.project.llmmig_paths.round_path.mkdir(parents=True, exist_ok=True)
        diff_command = f"kdiff3 '../{premig_paths.round_path.name}' '.'"
        self.project.llmmig_paths.round_path.joinpath(f"kdiff3.sh").write_text(diff_command)

    def set_round_report(self, round_report: MigRoundReport):
        full_report = self.project.get_report()
        full_report.llmmig = round_report
