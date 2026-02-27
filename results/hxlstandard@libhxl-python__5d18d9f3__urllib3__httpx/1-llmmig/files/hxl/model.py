"""Main data-model classes for the Humanitarian Exchange Language (HXL).

This module defines the basic classes for working with HXL data. Other
modules have classes derived from these (e.g. in
[hxl.filters](filters.html) or [hxl.input](io.html)). The core class is
[Dataset](#hxl.model.Dataset), which defines the operations available
on a HXL dataset, including convenience methods for chaining filters.

Typical usage:

    source = hxl.data("https://example.org/data.csv")
    # returns a hxl.model.Dataset object

    result = source.with_lines("#country+name=Kenya").sort()
    # a filtered/sorted view of the data


This code is released into the Public Domain and comes with NO WARRANTY.

"""

import abc, copy, csv, dateutil, hashlib, json, logging, operator, re, six

import hxl

from hxl.util import logup

import httpx  # Replaced urllib3 with httpx

logger = logging.getLogger(__name__)


# Cut off for fuzzy detection of a hashtag row
# At least this percentage of cells must parse as HXL hashtags
FUZZY_HASHTAG_PERCENTAGE = 0.5


class TagPattern(object):
    """Pattern for matching a HXL hashtag and attributes

    - the pattern "#*" matches any hashtag/attribute combination
    - the pattern "#*+foo" matches any hashtag with the foo attribute
    - the pattern "#tag" matches #tag with any attributes
    - the pattern "#tag+foo" matches #tag with foo among its attributes
    - the pattern "#tag-foo" matches #tag with foo *not* among its attributes
    - the pattern "#tag+foo-bar" matches #tag with foo but not bar
    - the pattern "#tag+foo+bar!" matches #tag with exactly the attributes foo and bar, but *no others*

    The normal way to create a tag pattern is using the
    [parse()](#hxl.model.TagPattern.parse) method rather than the
    constructor:

        pattern = hxl.model.TagPattern.parse("#affected+f-children")

    Args:
        tag: the basic hashtag (without attributes)
        include_attributes: a list of attributes that must be present
        exclude_attributes: a list of attributes that must not be present
        is_absolute: if True, no attributes are allowed except those in _include_attributes_

    """


    PATTERN = r'^\s*#?({token}|\*)((?:\s*[+-]{token})*)\s*(!)?\s*$'.format(token=hxl.datatypes.TOKEN_PATTERN)
    """Constant: regular expression to match a HXL tag pattern.
    """

    def __init__(self, tag, include_attributes=[], exclude_attributes=[], is_absolute=False):
        self.tag = tag

        self.include_attributes = set(include_attributes)
        """Set of all attributes that must be present"""

        self.exclude_attributes = set(exclude_attributes)
        """Set of all attributes that must not be present"""

        self.is_absolute = is_absolute
        """True if this pattern is absolute (no extra attributes allowed)"""

    def is_wildcard(self):
        return self.tag == '#*'

    def match(self, column):
        """Check whether a Column matches this pattern.
        @param column: the column to check
        @returns: True if the column is a match
        """
        if column.tag and (self.is_wildcard() or self.tag == column.tag):
            # all include_attributes must be present
            if self.include_attributes:
                for attribute in self.include_attributes:
                    if attribute not in column.attributes:
                        return False
            # all exclude_attributes must be absent
            if self.exclude_attributes:
                for attribute in self.exclude_attributes:
                    if attribute in column.attributes:
                        return False
            # if absolute, then only specified attributes may be present
            if self.is_absolute:
                for attribute in column.attributes:
                    if attribute not in self.include_attributes:
                        return False
            return True
        else:
            return False

    def get_matching_columns(self, columns):
        """Return a list of columns that match the pattern.
        @param columns: a list of L{hxl.model.Column} objects
        @returns: a list (possibly empty)
        """
        result = []
        for column in columns:
            if self.match(column):
                result.append(column)
        return result

    def find_column_index(self, columns):
        """Get the index of the first matching column.
        @param columns: a list of columns to check
        @returns: the 0-based index of the first matching column, or None for no match
        """
        for i in range(len(columns)):
            if self.match(columns[i]):
                return i
        return None

    def find_column(self, columns):
        """Check whether there is a match in a list of columns."""
        for column in columns:
            if self.match(column):
                return column
        return None

    def __repr__(self):
        s = self.tag
        if self.include_attributes:
            for attribute in self.include_attributes:
                s += '+' + attribute
        if self.exclude_attributes:
            for attribute in self.exclude_attributes:
                s += '-' + attribute
        return s

    __str__ = __repr__

    @staticmethod
    def parse(s):
        """Parse a single tag-pattern string.

            pattern = TagPattern.parse("#affected+f-children")

        The [parse_list()](#hxl.model.TagPattern.parse_list) method
        will call this method to parse multiple patterns at once.

        Args:
            s: the tag-pattern string to parse

        Returns:
            A TagPattern object

        """

        if not s:
            # edge case: null value
            raise hxl.HXLException('Attempt to parse empty tag pattern')
        elif isinstance(s, TagPattern):
            # edge case: already parsed
            return s

        result = re.match(TagPattern.PATTERN, s)
        if result:
            tag = '#' + result.group(1).lower()
            include_attributes = set()
            exclude_attributes = set()
            attribute_specs = re.split(r'\s*([+-])', result.group(2))
            for i in range(1, len(attribute_specs), 2):
                if attribute_specs[i] == '+':
                    include_attributes.add(attribute_specs[i + 1].lower())
                else:
                    exclude_attributes.add(attribute_specs[i + 1].lower())
            if result.group(3) == '!':
                is_absolute = True
                if exclude_attributes:
                    raise ValueError('Exclusions not allowed in absolute patterns')
            else:
                is_absolute = False
            return TagPattern(
                tag,
                include_attributes=include_attributes,
                exclude_attributes=exclude_attributes,
                is_absolute=is_absolute
            )
        else:
            raise hxl.HXLException('Malformed tag: ' + s)

    @staticmethod
    def parse_list(specs):
        """Parse a list of tag-pattern strings.

        If _specs_ is a list of already-parsed TagPattern objects, do
        nothing. If it's a list of strings, apply
        [parse()](#hxl.model.TagPattern.parse) to each one. If it's a
        single string with multiple patterns separated by commas,
        split the string, then parse the patterns.

            patterns = TagPattern.parse_list("#affected+f,#inneed+f")
            # or
            patterns = TagPattern.parse_list("#affected+f", "#inneed+f")

        Args:
            specs: the raw input (a list of strings, or a single string with commas separating the patterns)

        Returns:
            A list of TagPattern objects.

        """
        if not specs:
            return []
        if isinstance(specs, six.string_types):
            specs = specs.split(',')
        return [TagPattern.parse(spec) for spec in specs]

    @staticmethod
    def match_list(column, patterns):
        """Test if a column matches any of the patterns in a list.

        This is convenient to use together with [parse_list()](hxl.model.TagPattern.parse_list):

            patterns = TagPattern.parse_list(["#affected+f", "#inneed+f"])
            if TagPattern.match_list(column, patterns):
                print("The column matched one of the patterns")

        Args:
            column: the column to test
            patterns: a list of zero or more patterns.

        Returns:
            True if there is a match

        """
        for pattern in patterns:
            if pattern.match(column):
                return True
        return False
