
# MigrateLib: a tool for end-to-end Python library migration -- Artifacts

This repository contains the artifact of the paper - "MigrateLib: a tool for end-to-end Python library migration", submitted to EMSE.
The artifact contains the MigrateLib tool (`migratelib` directory), the code to run the experiments (`scripts` directory), and the results of the experiments (`results` directory).

This work is an extension of our previous conference paper "An Empirical Study of Python Library Migration Using Large Language Models", published at ASE 2024.
Artifact related to that prior work can be found at: https://figshare.com/articles/conference_contribution/25459000.

## Contents
Below are the main files and directories included in this artifact. A name ending with `/` indicates a directory. Any part within `<...>` is a placeholder that are to be replaced with specific values.

- `migratelib/` - the core migration tool code.
- `scripts/` - python scripts that use the migratelib tool to run migrations and evaluations. Also generates the figures we use in the paper.
- `results/` - detailed results of our experiments. Keep reading for details.
  - `<migration-id>` (*migdir*) - each of these directories contains the output of a single migration experiment, including transformed files and a detailed report. A migration id is encoded as `<repo-org>@<repo-name>__<commit-sha>__<source-lib>__<target-lib>`.
    - `report.yaml` - a summary report aggregating key metrics across all experiments. We describe the contents of this file later in this document.
    - `<step>/` - contains the test results of each step. All migrations include at least the `0-premig` and `1-llmmig` steps. Based on which post processing steps were applied, there may be a `2-merge_skipped` and/or a `3-async_transform` folders as well.
      - `files/` - Contains the source files after the corresponding step. The content inside this directory mimics the original repository structure, but includes only the files which are modified during the migration. The `0-premig/files/` folder contains the original source files before any migration steps.
      - `test-report.json` - the pytest results after running the test suite at the corresponding step.

## The `report.yaml` files
The `report.yaml` file in each experiment folder is the primary metadata file for that experiment.
Below is the description of the most relevant fields contained in the `report.yaml` file.
- `mig` - migration identifier string.
- `repo` - repository name.
- `commit` - full commit SHA of the repository in which the migration was performed.
- `source` - source library name.
- `target` - target library name.
- `<step>` - details about the a step. Can be `premig`, `llmmig`, `merge_skipped`, or `async_transform` depending on which steps were applied in the migration.
  - `name` - name of the step.
  - `files` - list of files modified during the migration at this step.
  - `test_diffs` - list of tests that changed result compared to the premig tests.
- `manual_edit` - indicates the results of the manual edits we applied to some migrations (see RQ-2.2 in the paper for details). The structure is similar to the `<step>` field described above.


