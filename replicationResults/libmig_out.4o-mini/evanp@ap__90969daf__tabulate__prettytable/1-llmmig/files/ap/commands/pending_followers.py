from .command import Command
from prettytable import PrettyTable


class PendingFollowersCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("pendingFollowers")
        slice = self.collection_slice(coll, self.offset, self.limit)
        table = PrettyTable()
        table.field_names = ["activity", "id", "name", "published"]
        
        for item in slice:
            activity = self.to_object(item, ["id", "actor", "published"])
            follower = self.to_object(
                activity["actor"],
                [
                    "id",
                    "preferredUsername",
                    ["name", "nameMap", "summary", "summaryMap"],
                ],
            )
            activity_id = self.to_id(activity)
            id = self.to_webfinger(follower)
            name = self.to_text(follower)
            published = activity["published"] if "published" in activity else None
            table.add_row([activity_id, id, name, published])
        
        print(table)
