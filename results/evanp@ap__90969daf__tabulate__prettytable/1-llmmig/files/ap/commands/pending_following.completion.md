### Explanation of Changes:
The original code uses the `tabulate` library to format and print a table. To migrate to the `prettytable` library, the following changes were made:
1. **Import Statement**: Replaced the import of `tabulate` with the import of `PrettyTable` from the `prettytable` library.
2. **Table Creation**: Instead of using `tabulate` to format the table, a `PrettyTable` object is created.
3. **Adding Headers**: The headers are set using the `field_names` attribute of the `PrettyTable` object.
4. **Adding Rows**: Rows are added to the `PrettyTable` object using the `add_row` method.
5. **Printing the Table**: The `PrettyTable` object is directly printed, as it automatically formats the table when converted to a string.

### Modified Code:
```python
from .command import Command
from prettytable import PrettyTable


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
        
        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = ["activity", "id", "name", "published"]
        
        # Add rows to the PrettyTable
        for row in rows:
            table.add_row(row)
        
        # Print the formatted table
        print(table)
```