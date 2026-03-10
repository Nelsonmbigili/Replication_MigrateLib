### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:

1. **Import Statement**: The import statement for `tabulate` was replaced with an import statement for `PrettyTable` from the `prettytable` library.
2. **Table Creation**: Instead of using `tabulate` to format the rows into a table, a `PrettyTable` object was created, and the headers were set using the `field_names` attribute.
3. **Adding Rows**: Each row of data was added to the `PrettyTable` object using the `add_row` method instead of appending to a list and passing it to `tabulate`.

Here is the modified code:

```python
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
        table = PrettyTable()
        table.field_names = ["id", "name"]
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
            table.add_row([id, name])
        print(table)
```