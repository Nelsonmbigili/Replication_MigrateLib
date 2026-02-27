### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library:
1. **Import Change**: Removed the import of `tabulate` and replaced it with `from prettytable import PrettyTable`.
2. **Table Creation**: Replaced the `tabulate` function call with the creation of a `PrettyTable` object.
3. **Adding Headers**: Used the `field_names` attribute of `PrettyTable` to set the headers.
4. **Adding Rows**: Used the `add_row` method of `PrettyTable` to add rows to the table.
5. **Printing the Table**: The `PrettyTable` object is directly printable, so no additional formatting is required.

### Modified Code
```python
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

        rows = []

        for item in shares_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            rows.append([id, actor, published])

        # Create a PrettyTable object and set headers
        table = PrettyTable()
        table.field_names = ["id", "actor", "published"]

        # Add rows to the PrettyTable
        for row in rows:
            table.add_row(row)

        # Print the PrettyTable
        print(table)
```