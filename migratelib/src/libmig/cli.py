from pathlib import Path

import typer
from typing_extensions import Annotated

from libmig.mig.libmig_runner import LibMigRunner
from libmig.project import Project

app = typer.Typer(pretty_exceptions_show_locals=False)


def version_callback(val: bool = False):
    if val:
        from importlib.metadata import version
        v = version("libmig")
        typer.echo(f"libmig version: {v}")
        raise typer.Exit()


@app.command()
def libmig(
        source: Annotated[str, typer.Argument(
            help="The source library from which to migrate"
        )] = None,
        target: Annotated[str, typer.Argument(
            help="The target library to which to migrate"
        )] = None,
        code_path: Annotated[Path, typer.Option(
            "--code-path", "--path", "--cp",
            exists=True,
            dir_okay=True,
            file_okay=False,
            readable=True,
            help="Path of the project to migrate."
        )] = Path.cwd(),
        test_root: Annotated[Path, typer.Option(
            "--test-root", "--tr",
            exists=True,
            dir_okay=True,
            file_okay=False,
            readable=True,
            help="Path from where the test should be run. Should be relative to the project path."
        )] = None,
        requirements_file_paths: Annotated[list[Path], typer.Option(
            "--requirements-file-path", "--rfp",
            exists=True,
            dir_okay=False,
            file_okay=True,
            readable=True,
            help="Path to the requirements file. If not provided, assumes code_path/requirements.txt."
        )] = None,
        use_cache: Annotated[bool, typer.Option(
            "--use-cache",
            help="Use cache for the migration."
        )] = True,
        force_rerun: Annotated[bool, typer.Option(
            "--force-rerun",
            help="Force rerun the migration. Even if the migration is already done."
        )] = False,
        max_files: Annotated[int, typer.Option(
            "--max-files",
            help="Maximum number of files to migrate. If more files are found, abort the migration."
        )] = 20,
        smart_skip_tests: Annotated[bool, typer.Option(
            "--smart-skip-tests", "--sst",
            help="Skip running tests if they are already done."
                 "Tests are considered to be run if all of these conditions satisfy:"
                 "  1. No new files are migrated "
                 "  2. test-report.json file exists"
                 "  3. cov-report.json both exists."
        )] = False,
        output_path: Annotated[Path, typer.Option(
            "--output", "--output-path", "--out", "-o",
            help="Output path for the migration. If relative, it is relative to the project path."
        )] = Path(".libmig"),
        llm: Annotated[str, typer.Option(
            "--llm",
            help="The client to use for the migration."
        )] = None,
        rounds: Annotated[list[str], typer.Option(
            "--rounds", "--r",
            help="The rounds to run."
        )] = None,
        repo: Annotated[str, typer.Option(
            "--repo",
            help="Name of the repository. If not provided, assumes the project directory name."
        )] = None,
        python_version: Annotated[str, typer.Option(
            "--python-version", "--pyv",
            help="Python version to use when setting up the virtual environment."
        )] = None,
):
    """
    Migrate a project from one library to another.
    """

    project = Project(
        source=source,
        target=target,
        code_path=code_path,
        test_root=test_root,
        requirements_file_paths=requirements_file_paths,
        use_cache=use_cache,
        force_rerun=force_rerun,
        max_files=max_files,
        smart_skip_tests=smart_skip_tests,
        output_path=output_path,
        llm=llm,
        rounds=rounds,
        repo=repo,
        python_version=python_version,
    )
    runner = LibMigRunner(project)
    runner.run()


if __name__ == "__main__":
    app()
