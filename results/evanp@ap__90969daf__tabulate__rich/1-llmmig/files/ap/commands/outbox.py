from .command import Command
import itertools
from rich.table import Table
from rich.console import Console


class OutboxCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        actor = self.logged_in_actor()
        if actor is None:
            raise Exception("Not logged in")
        outbox = actor.get("outbox", None)
        if outbox is None:
            raise Exception("No outbox found")
        outbox_id = self.to_id(outbox)
        slice = itertools.islice(
            self.items(outbox_id), self.offset, self.offset + self.limit
        )
        
        # Create a rich Table
        table = Table(title="Outbox Items")
        table.add_column("id", justify="left")
        table.add_column("type", justify="left")
        table.add_column("summary", justify="left")
        table.add_column("published", justify="left")
        
        for item in slice:
            id = self.to_id(item)
            type = item.get("type", None)
            summary = self.text_prop(item, "summary")
            published = item.get("published")
            table.add_row(str(id), str(type), str(summary), str(published))
        
        # Print the table using rich Console
        console = Console()
        console.print(table)
