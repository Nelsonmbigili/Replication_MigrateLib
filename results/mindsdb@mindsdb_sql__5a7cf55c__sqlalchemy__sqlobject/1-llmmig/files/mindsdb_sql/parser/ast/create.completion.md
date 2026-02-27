### Explanation of Changes:
To migrate the code from using `sqlalchemy` to `sqlobject`, the following changes were made:
1. **Removed `sqlalchemy` imports**: The `sqlalchemy` library and its `types` module were removed since they are no longer needed.
2. **Replaced `sqlalchemy` type checks with `sqlobject` types**: The `sqlalchemy.types` (e.g., `sa_types.Integer`, `sa_types.Float`, `sa_types.Text`) were replaced with equivalent `sqlobject` types (`IntCol`, `FloatCol`, `StringCol`).
3. **Updated type handling logic**: The logic for determining column types was updated to use `sqlobject`'s column types instead of `sqlalchemy` types.
4. **Preserved the original structure**: The rest of the code was left unchanged to ensure compatibility with the larger application.

### Modified Code:
```python
from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.utils import indent
from typing import List

try:
    from sqlobject import IntCol, FloatCol, StringCol
except ImportError:
    IntCol = FloatCol = StringCol = None


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

                if not isinstance(col.type, str) and IntCol is not None:
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

### Key Changes:
1. **Removed `sqlalchemy` imports**:
   ```python
   try:
       from sqlalchemy import types as sa_types
   except ImportError:
       sa_types = None
   ```
   was replaced with:
   ```python
   try:
       from sqlobject import IntCol, FloatCol, StringCol
   except ImportError:
       IntCol = FloatCol = StringCol = None
   ```

2. **Replaced `sqlalchemy` type checks**:
   The type-checking logic was updated to use `sqlobject` types:
   ```python
   if not isinstance(col.type, str) and sa_types is not None:
       if issubclass(col.type, sa_types.Integer):
           type = 'int'
       elif issubclass(col.type, sa_types.Float):
           type = 'float'
       elif issubclass(col.type, sa_types.Text):
           type = 'text'
   ```
   was replaced with:
   ```python
   if not isinstance(col.type, str) and IntCol is not None:
       if col.type == IntCol:
           type = 'int'
       elif col.type == FloatCol:
           type = 'float'
       elif col.type == StringCol:
           type = 'text'
   ```

These changes ensure the code now uses `sqlobject` instead of `sqlalchemy` while maintaining the original functionality.