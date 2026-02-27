### Explanation of Changes:
The original code uses the `tabulate` library to format and print a table. To migrate to the `prettytable` library:
1. Replace the `tabulate` import with `from prettytable import PrettyTable`.
2. Replace the `tabulate` function call with the creation and usage of a `PrettyTable` object.
3. Use the `field_names` attribute of `PrettyTable` to set the headers.
4. Use the `add_row` method of `PrettyTable` to add rows to the table.
5. Print the `PrettyTable` object directly instead of using the `tabulate` function.

### Modified Code:
```python
from .command import Command
import itertools
from prettytable import PrettyTable


class FollowingCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("following")
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
        
        # Add rows to the table
        for row in rows:
            table.add_row(row)
        
        # Print the table
        print(table)
```