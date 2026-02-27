from .command import Command
import itertools
from prettytable import PrettyTable


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
        table = PrettyTable()
        table.field_names = ["id", "type", "summary", "published"]
        for item in slice:
            id = self.to_id(item)
            type = item.get("type", None)
            summary = self.text_prop(item, "summary")
            published = item.get("published")
            table.add_row([id, type, summary, published])
        print(table)
