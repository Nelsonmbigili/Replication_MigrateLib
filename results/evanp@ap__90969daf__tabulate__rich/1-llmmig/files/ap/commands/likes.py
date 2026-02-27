from .command import Command
from rich.console import Console
from rich.table import Table

class LikesCommand(Command):
    """`likes` command"""

    def __init__(self, args, env):
        super().__init__(args, env)
        self.id = args.id
        self.limit = args.limit
        self.offset = args.offset

    def run(self):
        """Run the command"""

        obj = self.get_object(self.id)
        if obj is None:
            raise ValueError("Object not found")

        if "likes" not in obj:
            raise ValueError("Object has no likes")

        likes_id = self.to_id(obj["likes"])

        likes_slice = self.collection_slice(likes_id, self.offset, self.limit)

        # Create a rich Table
        table = Table(show_header=True, header_style="bold")
        table.add_column("id")
        table.add_column("actor")
        table.add_column("published")

        for item in likes_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            table.add_row(str(id), actor, str(published) if published else "")

        # Print the table using rich Console
        console = Console()
        console.print(table)
