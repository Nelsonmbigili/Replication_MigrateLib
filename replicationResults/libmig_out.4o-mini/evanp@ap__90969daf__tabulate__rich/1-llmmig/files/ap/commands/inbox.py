from .command import Command
import itertools
from rich.console import Console
from rich.table import Table
from requests.exceptions import HTTPError

class InboxCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit
        self.console = Console()  # Initialize the Console object

    def run(self):
        actor = self.logged_in_actor()
        if actor is None:
            raise Exception("Not logged in")
        inbox = actor.get("inbox", None)
        if inbox is None:
            raise Exception("No inbox found")
        inbox_id = self.to_id(inbox)
        slice = itertools.islice(
            self.items(inbox_id), self.offset, self.offset + self.limit
        )
        rows = []
        for item in slice:
            # Use the object as provided as fallback
            activity = self.to_object(item, [["actor", "attributedTo"], "type", "summary", "published", "id"])
            id = activity.get("id", None)
            type = activity.get("type", None)
            summary = self.text_prop(activity, "summary")
            published = activity.get("published", None)
            # Use the actor id as fallback
            actor_prop = activity.get("actor", activity.get("attributedTo", None))
            if actor_prop is None:
                actor = "<NONE>"
            else:
                actor = self.to_webfinger(actor_prop)
            rows.append([id, actor, type, summary, published])
        
        # Create a Rich Table
        table = Table(title="Inbox Items")
        table.add_column("id")
        table.add_column("actor")
        table.add_column("type")
        table.add_column("summary")
        table.add_column("published")

        for row in rows:
            table.add_row(*map(str, row))  # Add rows to the table

        self.console.print(table)  # Print the table using Rich
