### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:

1. **Import Statement**: The import statement for `tabulate` was replaced with an import statement for `PrettyTable` from the `prettytable` library.
2. **Table Creation**: Instead of using the `tabulate` function to format the rows into a table, a `PrettyTable` object was created, and the headers were set using the `field_names` attribute.
3. **Adding Rows**: Each row was added to the `PrettyTable` object using the `add_row` method instead of appending to a list and passing it to `tabulate`.

Here is the modified code:

```python
from .command import Command
from prettytable import PrettyTable
import json

class RepliesCommand(Command):
    """`replies` command"""

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

        if "replies" not in obj:
            raise ValueError("Object has no replies")

        replies_id = self.to_id(obj["replies"])

        replies_slice = self.collection_slice(replies_id, self.offset, self.limit)

        table = PrettyTable()
        table.field_names = ["id", "attributedTo", "content", "published"]

        for item in replies_slice:
            id = self.to_id(item)
            reply = self.to_object(item,
                                      ["attributedTo",
                                       "published",
                                       ["content", "contentMap"]])
            if "contentMap" not in reply:
                raise Exception(f'No contentMap in {id}')
            attributedTo = self.to_webfinger(reply["attributedTo"])
            published = reply.get("published")
            content = self.text_prop(reply, "content")
            if content is None:
                raise Exception(f'No content in {id}')
            table.add_row([id, attributedTo, content, published])

        print(table)
```