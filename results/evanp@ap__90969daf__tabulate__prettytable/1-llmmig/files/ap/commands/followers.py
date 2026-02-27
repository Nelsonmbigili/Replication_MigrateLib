from .command import Command
import itertools
from prettytable import PrettyTable


class FollowersCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("followers")
        slice = self.collection_slice(coll, self.offset, self.limit)
        rows = []
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
            rows.append([id, name])
        
        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = ["id", "name"]  # Set headers
        for row in rows:
            table.add_row(row)  # Add each row to the table
        
        print(table)  # Print the table
