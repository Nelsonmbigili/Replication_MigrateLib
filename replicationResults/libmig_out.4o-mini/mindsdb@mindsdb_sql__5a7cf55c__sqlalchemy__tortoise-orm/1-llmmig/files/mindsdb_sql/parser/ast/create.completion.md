### Explanation of Changes

To migrate the provided code from using SQLAlchemy to Tortoise-ORM, the following changes were made:

1. **Type Handling**: The type handling for columns was modified to use Tortoise-ORM's field types instead of SQLAlchemy's. Tortoise-ORM uses specific field classes like `fields.IntField`, `fields.FloatField`, and `fields.TextField` instead of the types from SQLAlchemy.

2. **Import Statements**: The import statements were updated to import the necessary types from Tortoise-ORM instead of SQLAlchemy.

3. **Type Checking**: The type checking logic in the `get_string` method was updated to check against Tortoise-ORM's field types.

4. **Field Attributes**: The handling of nullable fields was retained, but the logic was adapted to align with Tortoise-ORM's conventions.

Here is the modified code:

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

                if not isinstance(col.type, str) and fields is not None:
                    if isinstance(col.type, fields.IntField):
                        type = 'int'
                    elif isinstance(col.type, fields.FloatField):
                        type = 'float'
                    elif isinstance(col.type, fields.TextField):
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

This code now uses Tortoise-ORM's field types and maintains the original structure and functionality of the provided code.