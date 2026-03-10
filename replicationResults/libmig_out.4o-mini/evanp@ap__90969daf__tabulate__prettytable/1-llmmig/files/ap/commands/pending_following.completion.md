### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `from tabulate import tabulate` to `from prettytable import PrettyTable`.
2. **Table Creation**: Instead of using `tabulate` to format the rows into a table, a `PrettyTable` object was created to hold the data.
3. **Adding Headers**: The headers were added to the `PrettyTable` object using the `field_names` attribute.
4. **Adding Rows**: Each row of data was added to the `PrettyTable` object using the `add_row` method.

Here is the modified code:

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
        
        table = PrettyTable()
        table.field_names = ["activity", "id", "name", "published"]
        for row in rows:
            table.add_row(row)
        
        print(table)
```