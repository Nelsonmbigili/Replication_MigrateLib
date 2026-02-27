from .command import Command
import itertools
from rich.console import Console
from rich.table import Table


class FollowingCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("following")
        slice = self.collection_slice(coll, self.offset, self.limit)
        rows = []
        for item in slice:
            follower = self.to_object(
                item,
                [
                    "id",
                    "preferredUsername",
                    ["name", "nameMap", "summary", "summaryMap"],
                ],
            )
            id = self.to_webfinger(follower)
            name = self.to_text(follower)
            rows.append([id, name])

        # Create a table using rich
        table = Table()
        table.add_column("id", justify="left")
        table.add_column("name", justify="left")

        # Add rows to the table
        for row in rows:
            table.add_row(*row)

        # Print the table using rich
        console = Console()
        console.print(table)
