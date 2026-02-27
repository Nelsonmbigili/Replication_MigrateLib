import pytest
from cerberus import Validator

# Cerberus-compatible schema (converted from the original JSON schema)
IMPORT_SCHEMA = {
    'edition_name': {'type': 'string', 'required': False},
    'pagination': {'type': 'string', 'required': False},
    'title': {'type': 'string', 'required': True},
    'publishers': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
    'number_of_pages': {'type': 'integer', 'required': False},
    'languages': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
    'publish_date': {'type': 'string', 'required': False},
    'authors': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'birth_date': {'type': 'string', 'required': False},
                'personal_name': {'type': 'string', 'required': True},
                'death_date': {'type': 'string', 'required': False},
                'name': {'type': 'string', 'required': True},
                'entity_type': {'type': 'string', 'required': True},
            },
        },
        'required': True,
    },
    'by_statement': {'type': 'string', 'required': False},
    'publish_places': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'publish_country': {'type': 'string', 'required': False},
    'source_records': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
    'lccn': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'notes': {'type': 'string', 'required': False},
    'isbn_13': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'dewey_decimal_class': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'lc_classifications': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'oclc_numbers': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
    'isbn_10': {'type': 'list', 'schema': {'type': 'string'}, 'required': False},
}

# Examples taken from openlibrary/plugins/importapi/import_edition_builder.py
examples = [
    {
        'edition_name': '3rd ed.',
        'pagination': 'xii, 444 p.',
        'title': 'A course of pure mathematics',
        'publishers': ['At the University Press'],
        'number_of_pages': 444,
        'languages': ['eng'],
        'publish_date': '1921',
        'authors': [
            {
                'birth_date': '1877',
                'personal_name': 'Hardy, G. H.',
                'death_date': '1947',
                'name': 'Hardy, G. H.',
                'entity_type': 'person',
            }
        ],
        'by_statement': 'by G.H. Hardy',
        'publish_places': ['Cambridge'],
        'publish_country': 'enk',
        'source_records': ['test:example01'],
    },
    {
        'publishers': ['Ace Books'],
        'pagination': '271 p. ;',
        'title': 'Neuromancer',
        'lccn': ['91174394'],
        'notes': 'Hugo award book, 1985; Nebula award ; Philip K. Dick award',
        'number_of_pages': 271,
        'isbn_13': ['9780441569595'],
        'languages': ['eng'],
        'dewey_decimal_class': ['813/.54'],
        'lc_classifications': ['PS3557.I2264 N48 1984', 'PR9199.3.G53 N49 1984'],
        'publish_date': '1984',
        'publish_country': 'nyu',
        'authors': [
            {
                'birth_date': '1948',
                'personal_name': 'Gibson, William',
                'name': 'Gibson, William',
                'entity_type': 'person',
            }
        ],
        'by_statement': 'William Gibson',
        'oclc_numbers': ['24379880'],
        'publish_places': ['New York'],
        'isbn_10': ['0441569595'],
        'source_records': ['test:example02'],
    },
    {
        'publishers': ['Grosset & Dunlap'],
        'pagination': '156 p.',
        'title': 'Great trains of all time',
        'lccn': ['62051844'],
        'number_of_pages': 156,
        'languages': ['eng'],
        'dewey_decimal_class': ['625.2'],
        'lc_classifications': ['TF147 .H8'],
        'publish_date': '1962',
        'publish_country': 'nyu',
        'authors': [
            {
                'birth_date': '1894',
                'personal_name': 'Hubbard, Freeman H.',
                'name': 'Hubbard, Freeman H.',
                'entity_type': 'person',
            }
        ],
        'by_statement': 'Illustrated by Herb Mott',
        'oclc_numbers': ['1413013'],
        'publish_places': ['New York'],
        'source_records': ['test:example03'],
    },
]


@pytest.mark.parametrize('example', examples)
def test_import_examples(example):
    validator = Validator(IMPORT_SCHEMA)
    is_valid = validator.validate(example)
    assert is_valid, f"Validation failed: {validator.errors}"
