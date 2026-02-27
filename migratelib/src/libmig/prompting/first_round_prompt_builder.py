from libmig.project import Project
from libmig.prompting.prompt_builder_base import PromptBuilderBase
from libmig.utils.template import Template

_template = Template("""
The following Python code currently uses the library "<source-lib>" version <source-ver>.
Migrate this code to use the library "<target-lib>" version <target-ver> instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "<source-lib>" to "<target-lib>".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "<source-lib>" and "<target-lib>".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
<premig-code>
```
""".strip())


class FirstRoundPromptBuilder(PromptBuilderBase):
    def __init__(self, project: Project):
        self.project = project

    def build(self, file: str):
        project = self.project
        premig_code = project.premig_paths.read_code_file(file)
        premig_report = project.get_report().premig

        return _template.render({
            "source-lib": project.source,
            "target-lib": project.target,
            "source-ver": premig_report.source_version,
            "target-ver": premig_report.target_version,
            "premig-code": premig_code
        })
