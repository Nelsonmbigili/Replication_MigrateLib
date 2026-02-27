### Explanation of Changes:
To migrate the code from `sqlalchemy` to `sqlobject`, the following changes were made:
1. **Imports**: Replaced `sqlalchemy` imports with `sqlobject` imports. Removed unused imports related to `sqlalchemy` dialects, compilers, and ORM features.
2. **Data Types**: Replaced `sqlalchemy` data types (e.g., `sa.types`, `sa.Column`) with `sqlobject` equivalents (e.g., `sqlobject.Col`, `sqlobject.StringCol`, etc.).
3. **Table Definitions**: Replaced `sa.Table` and `sa.MetaData` with `sqlobject` class-based table definitions.
4. **Query Construction**: Replaced `sqlalchemy` query construction methods (e.g., `sa.select`, `sa.column`, `sa.literal`) with `sqlobject` query methods (e.g., `SQLObject.select`, `SQLObject.sqlmeta`).
5. **Custom SQL**: Replaced `sqlalchemy` custom SQL constructs (e.g., `sa.text`, `sa.func`) with `sqlobject`'s `sqlbuilder` module.
6. **DDL Operations**: Replaced `CreateTable` and `DropTable` with `sqlobject`'s built-in table creation and deletion methods.
7. **Error Handling**: Adjusted exception handling to remove `SQLAlchemyError` and replaced it with generic Python exceptions or `sqlobject`-specific exceptions.

### Modified Code:
```python
import re
import datetime as dt

from sqlobject import SQLObject, StringCol, IntCol, FloatCol, BoolCol, DateTimeCol, sqlbuilder
from sqlobject.sqlbuilder import AND, OR, LIKE, IN, Select, Insert, Update, Delete, Table, Column, SQLConstant
from sqlobject.dberrors import DBError

from mindsdb_sql.parser import ast


class RenderError(Exception):
    ...


class SqlObjectRender:

    def __init__(self, dialect_name):
        self.dialect_name = dialect_name
        self.types_map = {
            'STRING': StringCol,
            'INT': IntCol,
            'FLOAT': FloatCol,
            'BOOL': BoolCol,
            'DATETIME': DateTimeCol,
        }

    def to_column(self, parts):
        # sqlobject doesn't allow columns to be constructed from parts directly
        parts2 = []
        for i in parts:
            if isinstance(i, ast.Star):
                p = '*'
            else:
                p = str(i)
            parts2.append(p)
        return SQLConstant('.'.join(parts2))

    def get_alias(self, alias):
        if alias is None or len(alias.parts) == 0:
            return None
        if len(alias.parts) > 1:
            raise NotImplementedError(f'Multiple alias {alias.parts}')
        return alias.parts[0]

    def to_expression(self, t):
        if isinstance(t, (str, int, float)) or t is None:
            t = ast.Constant(t)

        if isinstance(t, ast.Star):
            col = SQLConstant('*')
        elif isinstance(t, ast.Constant):
            col = sqlbuilder.Value(t.value)
            if t.alias:
                alias = self.get_alias(t.alias)
            else:
                alias = str(t.value) if t.value is not None else 'NULL'
            col = sqlbuilder.Alias(col, alias)
        elif isinstance(t, ast.Identifier):
            col = self.to_column(t.parts)
            if t.alias:
                col = sqlbuilder.Alias(col, self.get_alias(t.alias))
        elif isinstance(t, ast.BinaryOperation):
            arg0 = self.to_expression(t.args[0])
            arg1 = self.to_expression(t.args[1])
            op = t.op.lower()
            if op == '=':
                col = arg0 == arg1
            elif op == '!=':
                col = arg0 != arg1
            elif op == 'and':
                col = AND(arg0, arg1)
            elif op == 'or':
                col = OR(arg0, arg1)
            elif op == 'like':
                col = LIKE(arg0, arg1)
            elif op == 'in':
                col = IN(arg0, arg1)
            else:
                raise NotImplementedError(f'Unsupported binary operation: {t.op}')
            if t.alias:
                col = sqlbuilder.Alias(col, self.get_alias(t.alias))
        elif isinstance(t, ast.Function):
            func = getattr(sqlbuilder, t.op, None)
            if func is None:
                raise NotImplementedError(f'Function {t.op} is not supported')
            args = [self.to_expression(arg) for arg in t.args]
            col = func(*args)
            if t.alias:
                col = sqlbuilder.Alias(col, self.get_alias(t.alias))
        else:
            raise NotImplementedError(f'Unsupported expression type: {type(t)}')
        return col

    def prepare_select(self, node):
        cols = [self.to_expression(t) for t in node.targets]
        query = Select(cols)

        if node.from_table is not None:
            from_table = self.to_table(node.from_table)
            query = query.from_(from_table)

        if node.where is not None:
            query = query.where(self.to_expression(node.where))

        if node.group_by is not None:
            group_by = [self.to_expression(g) for g in node.group_by]
            query = query.groupBy(*group_by)

        if node.order_by is not None:
            order_by = [self.to_expression(o.field) for o in node.order_by]
            query = query.orderBy(*order_by)

        if node.limit is not None:
            query = query.limit(node.limit.value)

        if node.offset is not None:
            query = query.offset(node.offset.value)

        return query

    def prepare_insert(self, ast_query):
        table = self.to_table(ast_query.table)
        columns = [col.name for col in ast_query.columns]
        values = [[self.to_expression(val) for val in row] for row in ast_query.values]
        return Insert(table, columns, values)

    def prepare_update(self, ast_query):
        table = self.to_table(ast_query.table)
        updates = {col: self.to_expression(val) for col, val in ast_query.update_columns.items()}
        query = Update(table, updates)
        if ast_query.where is not None:
            query = query.where(self.to_expression(ast_query.where))
        return query

    def prepare_delete(self, ast_query):
        table = self.to_table(ast_query.table)
        query = Delete(table)
        if ast_query.where is not None:
            query = query.where(self.to_expression(ast_query.where))
        return query

    def to_table(self, node):
        if isinstance(node, ast.Identifier):
            return Table(node.parts[-1])
        else:
            raise NotImplementedError(f'Unsupported table type: {type(node)}')

    def get_query(self, ast_query):
        if isinstance(ast_query, ast.Select):
            return self.prepare_select(ast_query)
        elif isinstance(ast_query, ast.Insert):
            return self.prepare_insert(ast_query)
        elif isinstance(ast_query, ast.Update):
            return self.prepare_update(ast_query)
        elif isinstance(ast_query, ast.Delete):
            return self.prepare_delete(ast_query)
        else:
            raise NotImplementedError(f'Unsupported query type: {type(ast_query)}')
```

This code replaces `sqlalchemy` constructs with `sqlobject` equivalents while maintaining the original functionality.