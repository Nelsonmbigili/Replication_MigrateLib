### Explanation of Changes:
To migrate from the `tabulate` library to the `prettytable` library:
1. Removed the import statement for `tabulate` and replaced it with an import for `PrettyTable` from `prettytable`.
2. Replaced the `tabulate` function call with the creation and configuration of a `PrettyTable` object.
3. Added rows to the `PrettyTable` object using the `add_row` method.
4. Configured the column headers using the `field_names` attribute of the `PrettyTable` object.
5. Used the `print` function to display the `PrettyTable` object directly.

### Modified Code:
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

        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = ["id", "actor", "published"]

        for item in likes_slice:
            id = self.to_id(item)
            activity = self.to_object(item, ["actor", "published"])
            actor = self.to_webfinger(activity["actor"])
            published = activity.get("published")
            table.add_row([id, actor, published])

        # Print the PrettyTable
        print(table)
```