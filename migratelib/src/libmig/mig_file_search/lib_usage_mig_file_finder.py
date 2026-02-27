from libmig.project import Project
from libmig.usage.lib_usage_detector import LibUsageDetector


class LibUsageMigFileFinder:
    def __init__(self, project: Project):
        self.project = project

    def find(self):
        project = self.project
        excluded_dirs = [".git", "__pycache__", "site-packages", "venv", ".venv", "build", "dist", ".libmig"]
        if project.out_is_in_project:
            excluded_dirs.append(project.output_path.name)

        detector = LibUsageDetector(project.code_path, excluded_dirs, project.source_lib.import_names)
        usages = detector.detect()
        return {u.file for u in usages}
