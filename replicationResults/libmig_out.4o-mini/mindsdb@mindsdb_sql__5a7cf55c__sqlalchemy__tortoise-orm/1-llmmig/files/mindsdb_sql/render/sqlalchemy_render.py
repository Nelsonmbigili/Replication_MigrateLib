import re
import datetime as dt

from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import Tortoise, run_async

from mindsdb_sql.parser import ast


class RenderError(Exception):
    ...


class INTERVAL:
    def __init__(self, info):
        self.info = info
        self.type = fields.IntervalField()

    def __str__(self):
        items = self.info.split(' ', maxsplit=1)
        items[0] = f"'{items[0]}'"
        return "INTERVAL " + " ".join(items)


class TortoiseRender:

    def __init__(self):
        self.types_map = {
            'BIGINT': fields.BigIntField,
            'FLOAT': fields.FloatField,
            'BOOLEAN': fields.BooleanField,
            'TEXT': fields.TextField,
            'VARCHAR': fields.CharField,
            'INT': fields.IntField,
            'DATE': fields.DateField,
            'DATETIME': fields.DatetimeField,
            'TIMESTAMP': fields.DatetimeField,
            'TIME': fields.TimeField,
            'INTERVAL': fields.IntervalField,
        }

    def to_column(self, parts):
        return '.'.join(parts)

    def get_alias(self, alias):
        if alias is None or len(alias.parts) == 0:
            return None
        if len(alias.parts) > 1:
            raise NotImplementedError(f'Multiple alias {alias.parts}')
        return alias.parts[0]

    def to_expression(self, t):
        if isinstance(t, str):
            return t
        elif isinstance(t, ast.Constant):
            return t.value
        elif isinstance(t, ast.Identifier):
            return self.to_column(t.parts)
        elif isinstance(t, ast.Function):
            return self.to_function(t)
        elif isinstance(t, ast.BinaryOperation):
            return self.prepare_binary_operation(t)
        elif isinstance(t, ast.UnaryOperation):
            return self.prepare_unary_operation(t)
        elif isinstance(t, ast.BetweenOperation):
            return self.prepare_between_operation(t)
        elif isinstance(t, ast.Interval):
            return INTERVAL(t.args[0])
        else:
            raise NotImplementedError(f'Column {t}')

    def prepare_binary_operation(self, t):
        left = self.to_expression(t.args[0])
        right = self.to_expression(t.args[1])
        return f"{left} {t.op} {right}"

    def prepare_unary_operation(self, t):
        arg = self.to_expression(t.args[0])
        return f"{t.op} {arg}"

    def prepare_between_operation(self, t):
        col = self.to_expression(t.args[0])
        lower = self.to_expression(t.args[1])
        upper = self.to_expression(t.args[2])
        return f"{col} BETWEEN {lower} AND {upper}"

    def to_function(self, t):
        func_name = t.op
        args = [self.to_expression(arg) for arg in t.args]
        return f"{func_name}({', '.join(args)})"

    def prepare_select(self, node):
        cols = [self.to_expression(t) for t in node.targets]
        query = f"SELECT {', '.join(cols)}"

        if node.from_table is not None:
            from_table = self.to_expression(node.from_table)
            query += f" FROM {from_table}"

        if node.where is not None:
            query += f" WHERE {self.to_expression(node.where)}"

        if node.group_by is not None:
            group_by = [self.to_expression(i) for i in node.group_by]
            query += f" GROUP BY {', '.join(group_by)}"

        if node.order_by is not None:
            order_by = [self.to_expression(f.field) for f in node.order_by]
            query += f" ORDER BY {', '.join(order_by)}"

        if node.limit is not None:
            query += f" LIMIT {node.limit.value}"

        if node.offset is not None:
            query += f" OFFSET {node.offset.value}"

        return query

    def get_query(self, ast_query):
        if isinstance(ast_query, ast.Select):
            return self.prepare_select(ast_query)
        else:
            raise NotImplementedError(f'Unknown statement: {ast_query.__class__.__name__}')

    def get_string(self, ast_query):
        return self.get_query(ast_query)


def render_dml_query(statement):
    return str(statement)


def render_ddl_query(statement):
    return str(statement)
