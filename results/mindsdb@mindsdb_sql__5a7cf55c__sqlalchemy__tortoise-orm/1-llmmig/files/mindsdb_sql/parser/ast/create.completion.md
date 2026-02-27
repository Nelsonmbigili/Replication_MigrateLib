### Explanation of Changes

To migrate the code from `sqlalchemy` to `tortoise-orm`, the following changes were made:

1. **Removed `sqlalchemy` Imports**: The `sqlalchemy` library and its type system (`sa_types`) were removed since `tortoise-orm` does not use them.
2. **Replaced `TableColumn` Type Handling**: The `tortoise-orm` type system was used to define column types. Instead of `sa_types.Integer`, `sa_types.Float`, etc., we now use `tortoise.fields` types like `IntField`, `FloatField`, `TextField`, etc.
3. **Updated `get_string` Method**: The logic for determining column types was updated to use `tortoise-orm` field types. The `nullable` and `length` attributes were handled similarly to the original code.
4. **Kept the Structure Intact**: The overall structure of the classes and methods was preserved to ensure compatibility with the rest of the application.

Below is the modified code.

---

### Modified Code
```python
from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.utils import indent
from typing import List

try:
    from tortoise import fields
except ImportError:
    fields = None


class TableColumn():
    def __init__(self, name, type='integer', length=None, default=None,
                 is_primary_key=False, nullable=None):
        self.name = name
        self.type = type
        self.is_primary_key = is_primary_key
        self.default = default
        self.length = length
        self.nullable = nullable

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        for k in ['name', 'is_primary_key', 'type', 'default', 'length']:

            if getattr(self, k) != getattr(other, k):
                return False

        return True


class CreateTable(ASTNode):
    def __init__(self,
                 name,
                 from_select=None,
                 columns: List[TableColumn] = None,
                 is_replace=False,
                 if_not_exists=False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.is_replace = is_replace
        self.from_select = from_select
        self.columns = columns
        self.if_not_exists = if_not_exists

    def to_tree(self, *args, level=0, **kwargs):
        ind = indent(level)
        ind1 = indent(level + 1)
        ind2 = indent(level + 2)

        replace_str = ''
        if self.is_replace:
            replace_str = f'{ind1}is_replace=True\n'

        from_select_str = ''
        if self.from_select is not None:
            from_select_str = f'{ind1}from_select={self.from_select.to_tree(level=level+1)}\n'

        columns_str = ''
        if self.columns is not None:
            columns = [
                f'{ind2}{col.name}: {col.type}'
                for col in self.columns
            ]

            columns_str = f'{ind1}columns=\n' + '\n'.join(columns)

        out_str = f'{ind}CreateTable(\n' \
                  f'{ind1}if_not_exists={self.if_not_exists},\n' \
                  f'{ind1}name={self.name}\n' \
                  f'{replace_str}' \
                  f'{from_select_str}' \
                  f'{columns_str}\n' \
                  f'{ind})\n'
        return out_str

    def get_string(self, *args, **kwargs):

        replace_str = ''
        if self.is_replace:
            replace_str = f' OR REPLACE'

        columns_str = ''
        if self.columns is not None:
            columns = []
            for col in self.columns:

                # Map tortoise-orm field types
                if not isinstance(col.type, str) and fields is not None:
                    if col.type == fields.IntField:
                        type = 'int'
                    elif col.type == fields.FloatField:
                        type = 'float'
                    elif col.type == fields.TextField:
                        type = 'text'
                else:
                    type = str(col.type)
                if col.length is not None:
                    type = f'{type}({col.length})'
                col_str = f'{col.name} {type}'
                if col.nullable is True:
                    col_str += ' NULL'
                elif col.nullable is False:
                    col_str += ' NOT NULL'
                columns.append(col_str)

            columns_str = '({})'.format(', '.join(columns))

        from_select_str = ''
        if self.from_select is not None:
            from_select_str = self.from_select.to_string()

        name_str = str(self.name)
        return f'CREATE{replace_str} TABLE {"IF NOT EXISTS " if self.if_not_exists else ""}{name_str} {columns_str} {from_select_str}'
```

---

### Key Notes:
- The `fields` module from `tortoise-orm` is used to replace `sqlalchemy.types`.
- The logic for determining column types in `get_string` was updated to check against `tortoise.fields` types.
- The rest of the code structure, including class and method names, was left unchanged to maintain compatibility with the larger application.