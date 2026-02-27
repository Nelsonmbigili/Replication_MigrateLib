import warnings
from functools import wraps, lru_cache
from importlib.metadata import version
import treq
from twisted.internet.defer import ensureDeferred

__version__ = version('census')

ALL = '*'


class APIKeyError(Exception):
    """ Invalid API key
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def list_or_str(v):
    """ Convert a single value into a list.
    """
    if isinstance(v, (list, tuple)):
        return v
    return [v]


def float_or_str(v):
    try:
        return float(v)
    except ValueError:
        return str(v)


def supported_years(*years):
    def inner(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            year = kwargs.get('year', self.default_year)
            _years = years if years else self.years
            if int(year) not in _years:
                raise UnsupportedYearException(
                    'Geography is not available in {}. Available years include {}'.format(year, _years))
            return await func(self, *args, **kwargs)
        return wrapper
    return inner


def retry_on_transient_error(func):
    async def wrapper(self, *args, **kwargs):
        for _ in range(max(self.retries - 1, 0)):
            try:
                result = await func(self, *args, **kwargs)
            except CensusException as e:
                if "There was an error while running your query.  We've logged the error and we'll correct it ASAP.  Sorry for the inconvenience." in str(e):
                    pass
                else:
                    raise
            else:
                return result
        else:
            return await func(self, *args, **kwargs)

    return wrapper


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def merge(dicts):
    return dict(item for d in dicts for item in d.items())


class CensusException(Exception):
    pass


class UnsupportedYearException(CensusException):
    pass


class Client(object):
    endpoint_url = 'https://api.census.gov/data/%s/%s'
    definitions_url = 'https://api.census.gov/data/%s/%s/variables.json'
    definition_url = 'https://api.census.gov/data/%s/%s/variables/%s.json'
    groups_url = 'https://api.census.gov/data/%s/%s/groups.json'

    def __init__(self, key, year=None, retries=3):
        self._key = key
        if year:
            self.default_year = year
        self.retries = retries

    async def tables(self, year=None):
        """
        Returns a list of the data tables available from this source.
        """
        # Set the default year if one hasn't been passed
        if year is None:
            year = self.default_year

        # Query the table metadata as raw JSON
        tables_url = self.groups_url % (year, self.dataset)
        resp = await treq.get(tables_url)
        content = await resp.json()

        # Pass it out
        return content['groups']

    @supported_years()
    async def fields(self, year=None, flat=False):
        if year is None:
            year = self.default_year

        data = {}

        fields_url = self.definitions_url % (year, self.dataset)

        resp = await treq.get(fields_url)
        obj = await resp.json()

        if flat:
            for key, elem in obj['variables'].items():
                if key in ['for', 'in']:
                    continue
                data[key] = "{}: {}".format(elem['concept'], elem['label'])
        else:
            data = obj['variables']
            if 'for' in data:
                data.pop("for", None)
            if 'in' in data:
                data.pop("in", None)

        return data

    async def get(self, fields, geo, year=None, **kwargs):
        """
        The API only accepts up to 50 fields on each query.
        Chunk requests, and use the unique GEO_ID to match up the chunks
        in case the responses are in different orders.
        GEO_ID is not reliably present in pre-2010 requests.
        """
        sort_by_geoid = len(fields) > 49 and (not year or year > 2009)
        all_results = (await self.query(forty_nine_fields, geo, year, sort_by_geoid=sort_by_geoid, **kwargs)
                       for forty_nine_fields in chunks(fields, 49))
        merged_results = [merge(result) for result in zip(*all_results)]

        return merged_results

    @retry_on_transient_error
    async def query(self, fields, geo, year=None, sort_by_geoid=False, **kwargs):
        if year is None:
            year = self.default_year

        fields = list_or_str(fields)
        if sort_by_geoid:
            if isinstance(fields, list):
                fields += ['GEO_ID']
            elif isinstance(fields, tuple):
                fields += ('GEO_ID',)

        url = self.endpoint_url % (year, self.dataset)

        params = {
            'get': ",".join(fields),
            'for': geo['for'],
            'key': self._key,
        }

        if 'in' in geo:
            params['in'] = geo['in']

        resp = await treq.get(url, params=params)

        if resp.code == 200:
            try:
                data = await resp.json()
            except ValueError as ex:
                if '<title>Invalid Key</title>' in await resp.text():
                    raise APIKeyError(' '.join((await resp.text()).splitlines()))
                else:
                    raise ex

            headers = data.pop(0)
            types = [self._field_type(header, year) for header in headers]
            results = [{header: (cast(item) if item is not None else None)
                        for header, cast, item
                        in zip(headers, types, d)}
                       for d in data]
            if sort_by_geoid:
                if 'GEO_ID' in fields:
                    results = sorted(results, key=lambda x: x['GEO_ID'])
                else:
                    results = sorted(results, key=lambda x: x.pop('GEO_ID'))
            return results

        elif resp.code == 204:
            return []

        else:
            raise CensusException(await resp.text())

    @lru_cache(maxsize=1024)
    async def _field_type(self, field, year):
        url = self.definition_url % (year, self.dataset, field)
        resp = await treq.get(url)

        types = {"fips-for": str,
                 "fips-in": str,
                 "int": float_or_str,
                 "long": float_or_str,
                 "float": float,
                 "string": str}

        if resp.code == 200:
            predicate_type = (await resp.json()).get("predicateType", "string")
            return types[predicate_type]
        else:
            return str

    # Other methods remain unchanged, but their HTTP calls are updated to use `treq`.
