from .command import Command
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

        rows = []

        for item in likes_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            rows.append([id, actor, published])

        table = Table(title="Likes")
        table.add_column("id", justify="right")
        table.add_column("actor")
        table.add_column("published")

        for row in rows:
            table.add_row(*row)

        print(table)
