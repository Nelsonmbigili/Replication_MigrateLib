### Explanation of Changes
To migrate the code from Flask to Sanic, the following changes were made:
1. **Abort Handling**: Flask's `abort` function is replaced with Sanic's `SanicException` for raising HTTP errors.
2. **Request Handling**: Flask's request handling is not directly visible in the provided code, so no changes were needed for request objects.
3. **Database Session**: The database session (`db.session`) remains unchanged as it is not tied to Flask or Sanic.
4. **Decorators**: The `arguments` and `response` decorators from `apifairy` are retained as they are independent of Flask or Sanic.
5. **HTTP Error Codes**: Sanic uses exceptions to handle HTTP errors, so `abort(400)` is replaced with `SanicException("Bad Request", status_code=400)`.

### Modified Code
```python
from functools import wraps
from sanic.exceptions import SanicException
from apifairy import arguments, response
import sqlalchemy as sqla
from api.app import db
from api.schemas import StringPaginationSchema, PaginatedCollection


def paginated_response(schema, max_limit=25, order_by=None,
                       order_direction='asc',
                       pagination_schema=StringPaginationSchema):
    def inner(f):
        @wraps(f)
        def paginate(*args, **kwargs):
            args = list(args)
            pagination = args.pop(-1)
            select_query = f(*args, **kwargs)
            if order_by is not None:
                o = order_by.desc() if order_direction == 'desc' else order_by
                select_query = select_query.order_by(o)

            count = db.session.scalar(sqla.select(
                sqla.func.count()).select_from(select_query.subquery()))

            limit = pagination.get('limit', max_limit)
            offset = pagination.get('offset')
            after = pagination.get('after')
            if limit > max_limit:
                limit = max_limit
            if after is not None:
                if offset is not None or order_by is None:  # pragma: no cover
                    raise SanicException("Bad Request", status_code=400)
                if order_direction != 'desc':
                    order_condition = order_by > after
                    offset_condition = order_by <= after
                else:
                    order_condition = order_by < after
                    offset_condition = order_by >= after
                query = select_query.limit(limit).filter(order_condition)
                offset = db.session.scalar(sqla.select(
                    sqla.func.count()).select_from(select_query.filter(
                        offset_condition).subquery()))
            else:
                if offset is None:
                    offset = 0
                if offset < 0 or (count > 0 and offset >= count) or limit <= 0:
                    raise SanicException("Bad Request", status_code=400)

                query = select_query.limit(limit).offset(offset)

            data = db.session.scalars(query).all()
            return {'data': data, 'pagination': {
                'offset': offset,
                'limit': limit,
                'count': len(data),
                'total': count,
            }}

        # wrap with APIFairy's arguments and response decorators
        return arguments(pagination_schema)(response(PaginatedCollection(
            schema, pagination_schema=pagination_schema))(paginate))

    return inner
```

### Key Points
- The `abort(400)` calls were replaced with `SanicException("Bad Request", status_code=400)`.
- No other changes were made to the logic, structure, or style of the code.
- The `apifairy` decorators and database session handling remain unchanged as they are not specific to Flask or Sanic.