from .command import Command
from rich.table import Table
from rich.console import Console


class PendingFollowingCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("pendingFollowing")
        slice = self.collection_slice(coll, self.offset, self.limit)
        rows = []
        for item in slice:
            activity = self.to_object(item, ["id", "object", "published"])
            followed = self.to_object(
                activity["object"],
                [
                    "id",
                    "preferredUsername",
                    ["name", "nameMap", "summary", "summaryMap"],
                ],
            )
            activity_id = self.to_id(activity)
            id = self.to_webfinger(followed)
            name = self.to_text(followed)
            published = activity["published"] if "published" in activity else None
            rows.append([activity_id, id, name, published])

        # Create a table using rich
        table = Table()
        table.add_column("activity")
        table.add_column("id")
        table.add_column("name")
        table.add_column("published")

        # Add rows to the table
        for row in rows:
            table.add_row(*[str(cell) if cell is not None else "" for cell in row])

        # Print the table using rich's Console
        console = Console()
        console.print(table)
