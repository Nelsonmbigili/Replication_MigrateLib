from .command import Command
from rich.console import Console
from rich.table import Table

class SharesCommand(Command):

    def __init__(self, args, env):
        super().__init__(args, env)
        self.id = args.id
        self.offset = args.offset
        self.limit = args.limit

    def run(self):

        obj = self.get_object(self.id)
        if obj is None:
            raise ValueError("Object not found")

        if "shares" not in obj:
            raise ValueError("Object has no shares")

        shares_id = self.to_id(obj["shares"])

        shares_slice = self.collection_slice(shares_id, self.offset, self.limit)

        # Create a rich Table
        table = Table()
        table.add_column("id")
        table.add_column("actor")
        table.add_column("published")

        for item in shares_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            table.add_row(id, actor, str(published))

        # Print the table using rich Console
        console = Console()
        console.print(table)
