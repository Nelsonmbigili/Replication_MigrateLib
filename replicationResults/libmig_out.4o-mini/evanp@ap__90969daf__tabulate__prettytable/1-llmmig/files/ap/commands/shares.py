from .command import Command
from prettytable import PrettyTable

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

        table = PrettyTable()
        table.field_names = ["id", "actor", "published"]

        for item in shares_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            table.add_row([id, actor, published])

        print(table)
