### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:

1. **Import Statement**: The import statement for `tabulate` was replaced with an import statement for `PrettyTable` from the `prettytable` library.
2. **Table Creation**: Instead of using `tabulate` to format the rows into a table, a `PrettyTable` object was created, and the headers were set using the `field_names` attribute.
3. **Adding Rows**: Each row of data was added to the `PrettyTable` object using the `add_row` method instead of appending to a list and passing it to `tabulate`.

Here is the modified code:

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

        table = PrettyTable()
        table.field_names = ["id", "actor", "published"]

        for item in shares_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            table.add_row([id, actor, published])

        print(table)
```