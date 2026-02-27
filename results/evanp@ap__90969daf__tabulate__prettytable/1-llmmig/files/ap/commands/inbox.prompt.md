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
from requests.exceptions import HTTPError

class InboxCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        actor = self.logged_in_actor()
        if actor is None:
            raise Exception("Not logged in")
        inbox = actor.get("inbox", None)
        if inbox is None:
            raise Exception("No inbox found")
        inbox_id = self.to_id(inbox)
        slice = itertools.islice(
            self.items(inbox_id), self.offset, self.offset + self.limit
        )
        rows = []
        for item in slice:
            # Use the object as provided as fallback
            activity = self.to_object(item, [["actor", "attributedTo"], "type", "summary", "published", "id"])
            id = activity.get("id", None)
            type = activity.get("type", None)
            summary = self.text_prop(activity, "summary")
            published = activity.get("published", None)
            # Use the actor id as fallback
            actor_prop = activity.get("actor", activity.get("attributedTo", None))
            if actor_prop is None:
                actor = "<NONE>"
            else:
                actor = self.to_webfinger(actor_prop)
            rows.append([id, actor, type, summary, published])
        print(tabulate(rows, headers=["id", "actor", "type", "summary", "published"]))

```