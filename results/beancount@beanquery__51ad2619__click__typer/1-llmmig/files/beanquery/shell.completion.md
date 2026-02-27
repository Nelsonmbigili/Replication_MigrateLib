### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Typer**: Replaced the `click` import with `typer`.
2. **Define Typer App**: Created a `typer.Typer()` app instance to replace the `@click.command` decorator.
3. **Command-Line Arguments and Options**:
   - Replaced `@click.argument` with function parameters in the `main` function.
   - Replaced `@click.option` with `typer.Option` for defining options.
   - Used `typer.Argument` for positional arguments.
4. **Version Option**: Replaced `@click.version_option` with `typer.Option` to handle the version display.
5. **Default Output File**: Adjusted the `output` option to use `typer.FileTextWrite` for file handling.
6. **Removed Click-Specific Decorators**: Removed all `click`-specific decorators and replaced them with equivalent `typer` constructs.

The rest of the code remains unchanged, as the migration only affects the command-line interface.

---

### Modified Code

```python
import typer

app = typer.Typer()

@app.command()
def main(
    filename: str = typer.Argument(..., help="Beancount ledger filename."),
    query: list[str] = typer.Argument(None, help="Beancount Query Language query."),
    numberify: bool = typer.Option(False, "--numberify", "-m", help="Numberify the output, removing the currencies."),
    format: str = typer.Option("text", "--format", "-f", help="Output format.", case_sensitive=False),
    output: typer.FileTextWrite = typer.Option("-", "--output", "-o", help="Output filename."),
    no_errors: bool = typer.Option(False, "--no-errors", "-q", help="Do not report errors."),
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda value: typer.echo(f"beanquery {beanquery.__version__}, beancount {beancount.__version__}") if value else None,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """An interactive interpreter for the Beancount Query Language.

    Load Beancount ledger FILENAME and run Beancount Query Language
    QUERY on it, if specified, or drop into the interactive shell. If
    not explicitly set with the dedicated option, the output format is
    inferred from the output file name, if specified.
    """
    # Create the shell.
    interactive = sys.stdin.isatty() and not query
    shell = BQLShell(filename, output, interactive, True, format, numberify)

    # Run interactively if we're a TTY and no query is supplied.
    if interactive:
        warnings.filterwarnings('always')
        shell.cmdloop()
    else:
        # Run in batch mode (Non-interactive).
        if query:
            # We have a query to run.
            query = ' '.join(query)
        else:
            # If we have no query and we're not a TTY, read the BQL command from
            # standard input.
            query = sys.stdin.read()

        shell.onecmd(query)

if __name__ == "__main__":
    app()
```

---

### Key Notes:
- The `typer` library simplifies the CLI definition by using function parameters and type hints.
- The `version` option is implemented using a callback to mimic the behavior of `@click.version_option`.
- The `output` option uses `typer.FileTextWrite` to handle file writing, similar to `click.File`.
- The rest of the application logic remains unchanged, ensuring compatibility with the existing codebase.