The following Python code currently uses the library "tabulate" version 0.9.0.
Migrate this code to use the library "prettytable" version 3.16.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tabulate" to "prettytable".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tabulate" and "prettytable".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from .command import Command
import itertools
from tabulate import tabulate


class OutboxCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        actor = self.logged_in_actor()
        if actor is None:
            raise Exception("Not logged in")
        outbox = actor.get("outbox", None)
        if outbox is None:
            raise Exception("No outbox found")
        outbox_id = self.to_id(outbox)
        slice = itertools.islice(
            self.items(outbox_id), self.offset, self.offset + self.limit
        )
        rows = []
        for item in slice:
            id = self.to_id(item)
            type = item.get("type", None)
            summary = self.text_prop(item, "summary")
            published = item.get("published")
            rows.append([id, type, summary, published])
        print(tabulate(rows, headers=["id", "type", "summary", "published"]))

```