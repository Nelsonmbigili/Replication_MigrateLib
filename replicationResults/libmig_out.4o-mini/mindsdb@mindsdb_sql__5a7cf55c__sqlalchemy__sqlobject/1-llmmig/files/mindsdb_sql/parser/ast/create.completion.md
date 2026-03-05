### Explanation of Changes

To migrate the code from using SQLAlchemy to SQLObject, the following changes were made:

1. **Import Statements**: The import statement for SQLAlchemy types was removed, as SQLObject does not require this import. Instead, we will use SQLObject's built-in types directly.
  
2. **Type Handling**: The type handling logic in the `get_string` method was modified to use SQLObject's types. SQLObject provides its own set of types, so we replaced the SQLAlchemy type checks with SQLObject equivalents.

3. **Type Definitions**: The type definitions for columns were adjusted to reflect SQLObject's way of defining types, which is different from SQLAlchemy.

4. **Removed Unused Imports**: Since SQLObject does not require the same import structure as SQLAlchemy, the conditional import for `sa_types` was removed.

The modified code reflects these changes while maintaining the original structure and functionality.

### Modified Code

```python
from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.utils import indent
from typing import List

from sqlobject import StringCol, IntCol, FloatCol, SQLObject

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

                if isinstance(col.type, str):
                    type = str(col.type)
                else:
                    if col.type == IntCol:
                        type = 'int'
                    elif col.type == FloatCol:
                        type = 'float'
                    elif col.type == StringCol:
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