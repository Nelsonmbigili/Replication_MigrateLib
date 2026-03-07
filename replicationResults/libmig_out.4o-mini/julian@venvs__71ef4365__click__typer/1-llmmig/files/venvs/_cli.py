import typer

from venvs import converge, create, find, remove, temporary

app = typer.Typer(help="Centralized virtual environments.")

app.command(name="converge")(converge.main)
app.command(name="create")(create.main)
app.command(name="find")(find.main)
app.command(name="remove")(remove.main)
app.command(name="temporary")(temporary.main)

if __name__ == "__main__":
    app()
