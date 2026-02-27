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


class PendingFollowingCommand(Command):
    def __init__(self, args, env):
        super().__init__(args, env)
        self.offset = args.offset
        self.limit = args.limit

    def run(self):
        coll = self.get_actor_collection("pendingFollowing")
        slice = self.collection_slice(coll, self.offset, self.limit)
        rows = []
        for item in slice:
            activity = self.to_object(item, ["id", "object", "published"])
            followed = self.to_object(
                activity["object"],
                [
                    "id",
                    "preferredUsername",
                    ["name", "nameMap", "summary", "summaryMap"],
                ],
            )
            activity_id = self.to_id(activity)
            id = self.to_webfinger(followed)
            name = self.to_text(followed)
            published = activity["published"] if "published" in activity else None
            rows.append([activity_id, id, name, published])
        print(tabulate(rows, headers=["activity", "id", "name", "published"]))

```