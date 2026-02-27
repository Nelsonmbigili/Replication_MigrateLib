The following Python code currently uses the library "tabulate" version 0.9.0.
Migrate this code to use the library "rich" version 14.0.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tabulate" to "rich".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tabulate" and "rich".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from .command import Command
from tabulate import tabulate

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

        print(tabulate(rows, headers=["id", "actor", "published"]))

```