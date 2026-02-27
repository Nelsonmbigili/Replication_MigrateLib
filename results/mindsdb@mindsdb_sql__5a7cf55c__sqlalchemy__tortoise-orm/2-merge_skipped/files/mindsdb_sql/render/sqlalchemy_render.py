import re
import datetime as dt
from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist, IntegrityError
from mindsdb_sql.parser import ast


class RenderError(Exception):
    ...


class BaseModel(Model):
    class Meta:
        abstract = True


class SqlalchemyRender:
    def __init__(self, dialect_name):
        self.dialect_name = dialect_name
        self.types_map = {
            "INT": fields.IntField,
            "BIGINT": fields.BigIntField,
            "FLOAT": fields.FloatField,
            "BOOLEAN": fields.BooleanField,
            "TEXT": fields.TextField,
            "CHAR": fields.CharField,
            "DATETIME": fields.DatetimeField,
            "DATE": fields.DateField,
            "TIME": fields.TimeField,
        }

    async def init_db(self, config):
        """
        Initialize the Tortoise ORM with the given configuration.
        """
        await Tortoise.init(config=config)
        await Tortoise.generate_schemas()

    def get_field(self, typename, **kwargs):
        """
        Map SQLAlchemy types to Tortoise-ORM fields.
        """
        typename = typename.upper()
        if re.match(r"^INT[\d]*$", typename):
            typename = "BIGINT"
        if re.match(r"^FLOAT[\d]*$", typename):
            typename = "FLOAT"
        field_class = self.types_map.get(typename)
        if not field_class:
            raise NotImplementedError(f"Unsupported type: {typename}")
        return field_class(**kwargs)

    async def create_table(self, table_name, columns):
        """
        Dynamically create a Tortoise-ORM model for a table.
        """
        attrs = {"__tablename__": table_name}
        for col in columns:
            field = self.get_field(col["type"], null=col.get("nullable", True))
            attrs[col["name"]] = field
        model = type(table_name, (BaseModel,), attrs)
        return model

    async def insert(self, model, values):
        """
        Insert values into a table.
        """
        try:
            await model.create(**values)
        except IntegrityError as e:
            raise RenderError(f"Insert failed: {e}")

    async def select(self, model, filters=None):
        """
        Select rows from a table.
        """
        try:
            if filters:
                return await model.filter(**filters).all()
            return await model.all()
        except DoesNotExist:
            return []

    async def update(self, model, filters, updates):
        """
        Update rows in a table.
        """
        try:
            await model.filter(**filters).update(**updates)
        except IntegrityError as e:
            raise RenderError(f"Update failed: {e}")

    async def delete(self, model, filters):
        """
        Delete rows from a table.
        """
        try:
            await model.filter(**filters).delete()
        except IntegrityError as e:
            raise RenderError(f"Delete failed: {e}")

    async def raw_query(self, query, params=None):
        """
        Execute a raw SQL query.
        """
        connection = Tortoise.get_connection("default")
        return await connection.execute_query(query, params)

    async def close_db(self):
    def get_alias(self, alias):
        if alias is None or len(alias.parts) == 0:
            return None
        if len(alias.parts) > 1:
            raise NotImplementedError(f'Multiple alias {alias.parts}')
        return alias.parts[0]

    def to_expression(self, t):

        # simple type
        if (
                isinstance(t, str)
                or isinstance(t, int)
                or isinstance(t, float)
                or t is None
        ):
            t = ast.Constant(t)

        if isinstance(t, ast.Star):
            col = sa.text('*')
        elif isinstance(t, ast.Last):
            col = self.to_column(['last'])
        elif isinstance(t, ast.Constant):
            col = sa.literal(t.value)
            if t.alias:
                alias = self.get_alias(t.alias)
            else:
                if t.value is None:
                    alias = 'NULL'
                else:
                    alias = str(t.value)
            col = col.label(alias)
        elif isinstance(t, ast.Identifier):
            # sql functions
            col = None
            if len(t.parts) == 1:
                name = t.parts[0].upper()
                if name == 'CURRENT_DATE':
                    col = sa_fnc.current_date()
                elif name == 'CURRENT_TIME':
                    col = sa_fnc.current_time()
                elif name == 'CURRENT_TIMESTAMP':
                    col = sa_fnc.current_timestamp()
                elif name == 'CURRENT_USER':
                    col = sa_fnc.current_user()
            if col is None:
                col = self.to_column(t.parts)
            if t.alias:
                col = col.label(self.get_alias(t.alias))
        elif isinstance(t, ast.Select):
            sub_stmt = self.prepare_select(t)
            col = sub_stmt.scalar_subquery()
            if t.alias:
                alias = self.get_alias(t.alias)
                col = col.label(alias)
        elif isinstance(t, ast.Function):
            fnc = self.to_function(t)
            if t.alias:
                alias = self.get_alias(t.alias)
            else:
                alias = str(t.op)
            col = fnc.label(alias)
        elif isinstance(t, ast.BinaryOperation):
            methods = {
                "+": "__add__",
                "-": "__sub__",
                "/": "__truediv__",
                "*": "__mul__",
                "%": "__mod__",
                "=": "__eq__",
                "!=": "__ne__",
                "<>": "__ne__",
                ">": "__gt__",
                "<": "__lt__",
                ">=": "__ge__",
                "<=": "__le__",
                "is": "is_",
                "is not": "is_not",
                "like": "like",
                "not like": "notlike",
                "in": "in_",
                "not in": "notin_",
                "||": "concat",
            }
            functions = {
                "and": sa.and_,
                "or": sa.or_,
            }

            arg0 = self.to_expression(t.args[0])
            arg1 = self.to_expression(t.args[1])

            op = t.op.lower()
            if op in ('in', 'not in'):
                if isinstance(arg1, sa.sql.selectable.ColumnClause):
                    raise NotImplementedError(f'Required list argument for: {op}')

            method = methods.get(op)
            if method is not None:
                sa_op = getattr(arg0, method)

                col = sa_op(arg1)
            elif t.op.lower() in functions:
                func = functions[t.op.lower()]
                col = func(arg0, arg1)
            else:
                col = arg0.op(t.op)(arg1)

            if t.alias:
                alias = self.get_alias(t.alias)
                col = col.label(alias)

        elif isinstance(t, ast.UnaryOperation):
            # not or munus
            opmap = {
                "NOT": "__invert__",
                "-": "__neg__",
            }
            arg = self.to_expression(t.args[0])

            method = opmap[t.op.upper()]
            col = getattr(arg, method)()
            if t.alias:
                alias = self.get_alias(t.alias)
                col = col.label(alias)

        elif isinstance(t, ast.BetweenOperation):
            col0 = self.to_expression(t.args[0])
            lim_down = self.to_expression(t.args[1])
            lim_up = self.to_expression(t.args[2])

            col = sa.between(col0, lim_down, lim_up)
        elif isinstance(t, ast.Interval):
            col = INTERVAL(t.args[0])
            if t.alias:
                alias = self.get_alias(t.alias)
                col = col.label(alias)

        elif isinstance(t, ast.WindowFunction):
            func = self.to_expression(t.function)

            partition = None
            if t.partition is not None:
                partition = [
                    self.to_expression(i)
                    for i in t.partition
                ]

            order_by = None
            if t.order_by is not None:
                order_by = []
                for f in t.order_by:
                    col0 = self.to_expression(f.field)
                    if f.direction == 'DESC':
                        col0 = col0.desc()
                    order_by.append(col0)

            col = sa.over(
                func,
                partition_by=partition,
                order_by=order_by
            )

            if t.alias:
                col = col.label(self.get_alias(t.alias))
        elif isinstance(t, ast.TypeCast):
            arg = self.to_expression(t.arg)
            type = self.get_type(t.type_name)
            if t.precision is not None:
                type = type(*t.precision)
            col = sa.cast(arg, type)

            if t.alias:
                alias = self.get_alias(t.alias)
                col = col.label(alias)
        elif isinstance(t, ast.Parameter):
            col = sa.column(t.value, is_literal=True)
            if t.alias: raise Exception()
        elif isinstance(t, ast.Tuple):
            col = [
                self.to_expression(i)
                for i in t.items
            ]
        elif isinstance(t, ast.Variable):
            col = sa.column(t.to_string(), is_literal=True)
        elif isinstance(t, ast.Latest):
            col = sa.column(t.to_string(), is_literal=True)
        elif isinstance(t, ast.Exists):
            sub_stmt = self.prepare_select(t.query)
            col = sub_stmt.exists()
        elif isinstance(t, ast.NotExists):
            sub_stmt = self.prepare_select(t.query)
            col = ~sub_stmt.exists()
        elif isinstance(t, ast.Case):
            col = self.prepare_case(t)
        else:
            # some other complex object?
            raise NotImplementedError(f'Column {t}')

        return col

    def prepare_case(self, t: ast.Case):
        conditions = []
        for condition, result in t.rules:
            conditions.append(
                (self.to_expression(condition), self.to_expression(result))
            )
        default = None
        if t.default is not None:
            default = self.to_expression(t.default)

        value = None
        if t.arg is not None:
            value = self.to_expression(t.arg)

        return sa.case(*conditions, else_=default, value=value)

    def to_function(self, t):
        op = getattr(sa.func, t.op)
        if t.from_arg is not None:
            arg = t.args[0].to_string()
            from_arg = self.to_expression(t.from_arg)

            fnc = op(arg, from_arg)
        else:
            args = [
                self.to_expression(i)
                for i in t.args
            ]
            if t.distinct:
                # set first argument to distinct
                args[0] = args[0].distinct()
            fnc = op(*args)
        return fnc

    def get_type(self, typename):
        # TODO how to get type
        if not isinstance(typename, str):
            # sqlalchemy type
            return typename

        typename = typename.upper()
        if re.match('^INT[\d]*$', typename):
            typename = 'BIGINT'
        if re.match('^FLOAT[\d]*$', typename):
            typename = 'FLOAT'
        type = self.types_map[typename]
        return type

    def prepare_join(self, join):
        # join tree to table list

        if isinstance(join.right, ast.Join):
            raise NotImplementedError('Wrong join AST')

        items = []

        if isinstance(join.left, ast.Join):
            # dive to next level
            items.extend(self.prepare_join(join.left))
        else:
            # this is first table
            items.append(dict(
                table=join.left
            ))

        # all properties set to right table
        items.append(dict(
            table=join.right,
            join_type=join.join_type,
            is_implicit=join.implicit,
            condition=join.condition
        ))

        return items

    def get_table_name(self, table_name):
        schema = None
        if isinstance(table_name, ast.Identifier):
            parts = table_name.parts

            if len(parts) > 2:
                # TODO tests is failing
                raise NotImplementedError(f'Path to long: {table_name.parts}')

            if len(parts) == 2:
                schema = parts[-2]

            table_name = parts[-1]

        return schema, table_name

    def to_table(self, node):
        if isinstance(node, ast.Identifier):
            schema, table_name = self.get_table_name(node)

            table = sa.table(table_name, schema=schema)

            if node.alias:
                table = aliased(table, name=self.get_alias(node.alias))

        elif isinstance(node, (ast.Select, ast.Union, ast.Intersect, ast.Except)):
            sub_stmt = self.prepare_select(node)
            alias = None
            if node.alias:
                alias = self.get_alias(node.alias)
            table = sub_stmt.subquery(alias)

        else:
            # TODO tests are failing
            raise NotImplementedError(f'Table {node.__name__}')

        return table

    def prepare_select(self, node):
        if isinstance(node, (ast.Union, ast.Except, ast.Intersect)):
            return self.prepare_union(node)

        cols = []
        for t in node.targets:
            col = self.to_expression(t)
            cols.append(col)

        query = sa.select(*cols)

        if node.cte is not None:
            for cte in node.cte:
                if cte.columns is not None and len(cte.columns) > 0:
                    raise NotImplementedError('CTE columns')

                stmt = self.prepare_select(cte.query)
                alias = cte.name

                query = query.add_cte(stmt.cte(self.get_alias(alias), nesting=True))

        if node.distinct:
            query = query.distinct()

        if node.from_table is not None:
            from_table = node.from_table

            if isinstance(from_table, ast.Join):
                join_list = self.prepare_join(from_table)
                # first table
                table = self.to_table(join_list[0]['table'])
                query = query.select_from(table)

                # other tables
                for item in join_list[1:]:
                    table = self.to_table(item['table'])
                    if item['is_implicit']:
                        # add to from clause
                        query = query.select_from(table)
                    else:
                        if item['condition'] is None:
                            # otherwise, sqlalchemy raises "Don't know how to join to ..."
                            condition = sa.text('1=1')
                        else:
                            condition = self.to_expression(item['condition'])

                        join_type = item['join_type']
                        method = 'join'
                        is_full = False
                        if join_type == 'LEFT JOIN':
                            method = 'outerjoin'
                        if join_type == 'FULL JOIN':
                            is_full = True

                        # perform join
                        query = getattr(query, method)(
                            table,
                            condition,
                            full=is_full
                        )
            elif isinstance(from_table, ast.Union):
                alias = None
                if from_table.alias:
                    alias = self.get_alias(from_table.alias)
                table = self.prepare_union(from_table).subquery(alias)
                query = query.select_from(table)

            elif isinstance(from_table, ast.Select):
                table = self.to_table(from_table)
                query = query.select_from(table)

            elif isinstance(from_table, ast.Identifier):
                table = self.to_table(from_table)
                query = query.select_from(table)

            elif isinstance(from_table, ast.NativeQuery):
                alias = None
                if from_table.alias:
                    alias = from_table.alias.parts[-1]
                table = sa.text(from_table.query).columns().subquery(alias)
                query = query.select_from(table)
            else:
                raise NotImplementedError(f'Select from {from_table}')

        if node.where is not None:
            query = query.filter(
                self.to_expression(node.where)
            )

        if node.group_by is not None:
            cols = [
                self.to_expression(i)
                for i in node.group_by
            ]
            query = query.group_by(*cols)

        if node.having is not None:
            query = query.having(self.to_expression(node.having))

        if node.order_by is not None:
            order_by = []
            for f in node.order_by:
                col0 = self.to_expression(f.field)
                if f.direction.upper() == 'DESC':
                    col0 = col0.desc()
                elif f.direction.upper() == 'ASC':
                    col0 = col0.asc()
                if f.nulls.upper() == 'NULLS FIRST':
                    col0 = sa.nullsfirst(col0)
                elif f.nulls.upper() == 'NULLS LAST':
                    col0 = sa.nullslast(col0)
                order_by.append(col0)

            query = query.order_by(*order_by)

        if node.limit is not None:
            query = query.limit(node.limit.value)

        if node.offset is not None:
            query = query.offset(node.offset.value)

        if node.mode is not None:
            if node.mode == 'FOR UPDATE':
                query = query.with_for_update()
            else:
                raise NotImplementedError(f'Select mode: {node.mode}')

        return query

    def prepare_union(self, from_table):
        step1 = self.prepare_select(from_table.left)
        step2 = self.prepare_select(from_table.right)

        if isinstance(from_table, ast.Except):
            func = sa.except_ if from_table.unique else sa.except_all
        elif isinstance(from_table, ast.Intersect):
            func = sa.intersect if from_table.unique else sa.intersect_all
        else:
            func = sa.union if from_table.unique else sa.union_all

        return func(step1, step2)

    def prepare_create_table(self, ast_query):
        columns = []

        for col in ast_query.columns:
            default = None
            if col.default is not None:
                if isinstance(col.default, str):
                    default = sa.text(col.default)

            if isinstance(col.type, str) and col.type.lower() == 'serial':
                col.is_primary_key = True
                col.type = 'INT'

            kwargs = {
                'primary_key': col.is_primary_key,
                'server_default': default,
            }
            if col.nullable is not None:
                kwargs['nullable'] = col.nullable

            columns.append(
                sa.Column(
                    col.name,
                    self.get_type(col.type),
                    **kwargs
                )
            )

        schema, table_name = self.get_table_name(ast_query.name)

        metadata = sa.MetaData()
        table = sa.Table(
            table_name,
            metadata,
            schema=schema,
            *columns
        )

        return CreateTable(table)

    def prepare_drop_table(self, ast_query):
        if len(ast_query.tables) != 1:
            raise NotImplementedError('Only one table is supported')

        schema, table_name = self.get_table_name(ast_query.tables[0])

        metadata = sa.MetaData()
        table = sa.Table(
            table_name,
            metadata,
            schema=schema
        )
        return DropTable(table, if_exists=ast_query.if_exists)

    def prepare_insert(self, ast_query, with_params=False):
        params = None
        schema, table_name = self.get_table_name(ast_query.table)

        names = []
        columns = []

        if ast_query.columns is None:
            raise NotImplementedError('Columns is required in insert query')
        for col in ast_query.columns:
            columns.append(
                sa.Column(
                    col.name,
                    # self.get_type(col.type)
                )
            )
            # check doubles
            if col.name in names:
                raise RenderError(f'Columns name double: {col.name}')
            names.append(col.name)

        table = sa.table(table_name, schema=schema, *columns)

        if ast_query.values is not None:
            values = []

            if ast_query.is_plain and with_params:

                for i in range(len(ast_query.columns)):
                    values.append(sa.column('%s', is_literal=True))

                values = [values]
                params = ast_query.values
            else:

                for row in ast_query.values:
                    row = [
                        self.to_expression(val)
                        for val in row
                    ]
                    values.append(row)

            stmt = table.insert().values(values)
        else:
            # is insert from subselect
            subquery = self.prepare_select(ast_query.from_select)
            stmt = table.insert().from_select(names, subquery)

        return stmt, params

    def prepare_update(self, ast_query):
        if ast_query.from_select is not None:
            raise NotImplementedError('Render of update with sub-select is not implemented')

        schema, table_name = self.get_table_name(ast_query.table)

        columns = []

        to_update = {}
        for col, value in ast_query.update_columns.items():
            columns.append(
                sa.Column(
                    col,
                )
            )

            to_update[col] = self.to_expression(value)

        table = sa.table(table_name, schema=schema, *columns)

        stmt = table.update().values(**to_update)

        if ast_query.where is not None:
            stmt = stmt.where(self.to_expression(ast_query.where))

        return stmt

    def prepare_delete(self, ast_query: ast.Delete):
        schema, table_name = self.get_table_name(ast_query.table)

        columns = []

        table = sa.table(table_name, schema=schema, *columns)

        stmt = table.delete()

        if ast_query.where is not None:
            stmt = stmt.where(self.to_expression(ast_query.where))

        return stmt

    def get_query(self, ast_query, with_params=False):
        params = None
        if isinstance(ast_query, (ast.Select, ast.Union, ast.Except, ast.Intersect)):
            stmt = self.prepare_select(ast_query)
        elif isinstance(ast_query, ast.Insert):
            stmt, params = self.prepare_insert(ast_query, with_params=with_params)
        elif isinstance(ast_query, ast.Update):
            stmt = self.prepare_update(ast_query)
        elif isinstance(ast_query, ast.Delete):
            stmt = self.prepare_delete(ast_query)
        elif isinstance(ast_query, ast.CreateTable):
            stmt = self.prepare_create_table(ast_query)
        elif isinstance(ast_query, ast.DropTables):
            stmt = self.prepare_drop_table(ast_query)
        else:
            raise NotImplementedError(f'Unknown statement: {ast_query.__class__.__name__}')
        return stmt, params

    def get_string(self, ast_query, with_failback=True):
        """
        Close the Tortoise ORM connection.
        """
        await Tortoise.close_connections()
        sql, _ = self.get_exec_params(ast_query, with_failback=with_failback, with_params=False)
        return sql

    def get_exec_params(self, ast_query, with_failback=True, with_params=True):
        """
        Render query with separated parameters and placeholders
        :param ast_query: query to render
        :param with_failback: switch to standard render in case of error
        :return: sql query and parameters
        """

        if isinstance(ast_query, (ast.CreateTable, ast.DropTables)):
            render_func = render_ddl_query
        else:
            render_func = render_dml_query

        try:
            stmt, params = self.get_query(ast_query, with_params=with_params)

            sql = render_func(stmt, self.dialect)

            return sql, params

        except (SQLAlchemyError, NotImplementedError) as e:
            if not with_failback:
                raise e

            sql_query = str(ast_query)
            if self.dialect.name == 'postgresql':
                sql_query = sql_query.replace('`', '')
            return sql_query, None


def render_dml_query(statement, dialect):

    class LiteralCompiler(dialect.statement_compiler):

        def render_literal_value(self, value, type_):

            if isinstance(value, (str, dt.date, dt.datetime, dt.timedelta)):
                return "'{}'".format(str(value).replace("'", "''"))

            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return str(LiteralCompiler(dialect, statement, compile_kwargs={'literal_binds': True}))


def render_ddl_query(statement, dialect):
    class LiteralCompiler(dialect.ddl_compiler):

        def render_literal_value(self, value, type_):
            if isinstance(value, (str, dt.date, dt.datetime, dt.timedelta)):
                return "'{}'".format(str(value).replace("'", "''"))

            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return str(LiteralCompiler(dialect, statement, compile_kwargs={'literal_binds': True}))