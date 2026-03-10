### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:
1. The import statement for `tabulate` was replaced with an import statement for `PrettyTable` from the `prettytable` library.
2. The `tabulate` function call was replaced with the creation of a `PrettyTable` object. The headers were set using the `field_names` attribute, and the rows were added using the `add_row` method.

### Modified Code
```python
from .command import Command
from prettytable import PrettyTable

class LikesCommand(Command):
    """`likes` command"""

    def __init__(self, args, env):
        super().__init__(args, env)
        self.id = args.id
        self.limit = args.limit
        self.offset = args.offset

    def run(self):
        """Run the command"""

        obj = self.get_object(self.id)
        if obj is None:
            raise ValueError("Object not found")

        if "likes" not in obj:
            raise ValueError("Object has no likes")

        likes_id = self.to_id(obj["likes"])

        likes_slice = self.collection_slice(likes_id, self.offset, self.limit)

        rows = []

        for item in likes_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            rows.append([id, actor, published])

        table = PrettyTable()
        table.field_names = ["id", "actor", "published"]
        for row in rows:
            table.add_row(row)

        print(table)
```