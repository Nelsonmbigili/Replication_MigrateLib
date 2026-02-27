import plac

def main(
    filename: str,
    *query: str,
    numberify: ("Numberify the output, removing the currencies.", "flag", "m") = False,
    format: ("Output format.", "option", "f", str) = 'text',
    output: ("Output filename.", "option", "o", plac.File) = '-',
    no_errors: ("Do not report errors.", "flag", "q") = False
):
    """An interactive interpreter for the Beancount Query Language.

    Load Beancount ledger FILENAME and run Beancount Query Language
    QUERY on it, if specified, or drop into the interactive shell. If
    not explicitly set with the dedicated option, the output format is
    inferred from the output file name, if specified.
    """
    import sys
    import warnings
    import beancount
    import beanquery
    from beanquery import BQLShell

    # Print version information manually
    print(f'beanquery {beanquery.__version__}, beancount {beancount.__version__}')

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
    plac.call(main)
