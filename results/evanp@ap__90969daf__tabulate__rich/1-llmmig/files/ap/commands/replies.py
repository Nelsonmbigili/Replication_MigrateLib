from .command import Command
from rich.table import Table
from rich.console import Console
import json

class RepliesCommand(Command):
    """`replies` command"""

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

        if "replies" not in obj:
            raise ValueError("Object has no replies")

        replies_id = self.to_id(obj["replies"])

        replies_slice = self.collection_slice(replies_id, self.offset, self.limit)

        rows = []

        for item in replies_slice:
            id = self.to_id(item)
            reply = self.to_object(item,
                                      ["attributedTo",
                                       "published",
                                       ["content", "contentMap"]])
            if "contentMap" not in reply:
                raise Exception(f'No contentMap in {id}')
            attributedTo = self.to_webfinger(reply["attributedTo"])
            published = reply.get("published")
            content = self.text_prop(reply, "content")
            if content is None:
                raise Exception(f'No content in {id}')
            rows.append([id, attributedTo, content, published])

        # Create a table using rich
        table = Table(title="Replies")

        # Add headers
        table.add_column("id", justify="left")
        table.add_column("attributedTo", justify="left")
        table.add_column("content", justify="left")
        table.add_column("published", justify="left")

        # Add rows to the table
        for row in rows:
            table.add_row(*row)

        # Render the table to the console
        console = Console()
        console.print(table)
