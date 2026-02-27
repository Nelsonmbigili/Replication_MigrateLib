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
        """
        Close the Tortoise ORM connection.
        """
        await Tortoise.close_connections()
