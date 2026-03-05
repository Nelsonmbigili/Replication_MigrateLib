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
        console = Console()
        table = Table(title="Following List")
        table.add_column("id", justify="left")
        table.add_column("name", justify="left")

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
            table.add_row(id, name)

        console.print(table)
