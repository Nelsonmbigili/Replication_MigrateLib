LibMig is a CLI to migrate your python project from one library to another.
It uses a large language model to do an initial migration, then applies additional changes to fix any issues.

Note that this is a work in progress and is not yet ready for production use.
However, it should still work for most cases.

## Installation
First clone this repo, and then install `libmig` using pip:

```bash
git clone https://github.com/ualberta-smr/LibMig
cd LibMig
pip install .
```

## Usage
Let's say you have a python git repository in the path `my-app`.
It uses `requests` and you want to migrate it to `httpx`.
You would run the following command:

```bash
libmig requests httpx --code-path=my-app
```

Below is the list of all available options. Run `libmig --help` to see this list.

```                                                                                                                                                         
 Usage: libmig [OPTIONS] [SOURCE] [TARGET]                                     
                                                                               
 Migrate a project from one library to another.                                

+- Arguments -----------------------------------------------------------------+
|   source      [SOURCE]  The source library from which to migrate            |
|                         [default: None]                                     |
|   target      [TARGET]  The target library to which to migrate              |
|                         [default: None]                                     |
+-----------------------------------------------------------------------------+
+- Options -------------------------------------------------------------------+
| --code-path,--path,--cp              DIRECTORY  Path of the project to      |
|                                                 migrate.                    |
|                                                 [default: .]                |
| --test-root,--tr                     DIRECTORY  Path from where the test    |
|                                                 should be run. Should be    |
|                                                 relative to the project     |
|                                                 path.                       |
|                                                 [default: None]             |
| --requirements-file-path,--rfp       FILE       Path to the requirements    |
|                                                 file. If not provided,      |
|                                                 assumes                     |
|                                                 code_path/requirements.txt. |
|                                                 [default: None]             |
| --use-cache                                     Use cache for the           |
|                                                 migration.                  |
|                                                 [default: True]             |
| --force-rerun                                   Force rerun the migration.  |
|                                                 Even if the migration is    |
|                                                 already done.               |
| --max-files                          INTEGER    Maximum number of files to  |
|                                                 migrate. If more files are  |
|                                                 found, abort the migration. |
|                                                 [default: 20]               |
| --smart-skip-tests,--sst                        Skip running tests if they  |
|                                                 are already done.Tests are  |
|                                                 considered to be run if all |
|                                                 of these conditions         |
|                                                 satisfy:  1. No new files   |
|                                                 are migrated   2.           |
|                                                 test-report.json file       |
|                                                 exists  3. cov-report.json  |
|                                                 both exists.                |
| --output,--output-path,--out, -o     PATH       Output path for the         |
|                                                 migration. If relative, it  |
|                                                 is relative to the project  |
|                                                 path.                       |
|                                                 [default: .libmig]          |
| --llm                                TEXT       The client to use for the   |
|                                                 migration.                  |
|                                                 [default: None]             |
| --rounds,--r                         INTEGER    The rounds to run.          |
|                                                 [default: None]             |
| --repo                               TEXT       Name of the repository. If  |
|                                                 not provided, assumes the   |
|                                                 project directory name.     |
|                                                 [default: None]             |
| --python-version,--pyv               TEXT       Python version to use when  |
|                                                 setting up the virtual      |
|                                                 environment.                |
|                                                 [default: None]             |
| --install-completion                            Install completion for the  |
|                                                 current shell.              |
| --show-completion                               Show completion for the     |
|                                                 current shell, to copy it   |
|                                                 or customize the            |
|                                                 installation.               |
| --help                                          Show this message and exit. |
+-----------------------------------------------------------------------------+
```

