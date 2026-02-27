import re


def find_member_name_from_error(error_message: str):
    if error_message.startswith("TypeError: "):
        return find_member_name_from_type_error(error_message)
    elif error_message.startswith("AttributeError: "):
        return error_message.split("'")[1]

    return None


def find_member_name_from_type_error(error_message: str):
    #  1a. TypeError: foo() missing n required positional argument: 'bar'
    #  1b. TypeError: foo() got an unexpected keyword argument 'bar'
    #  1c: TypeError: foo() takes no arguments
    #  2a. TypeError: 'classname' object cannot be interpreted as an integer
    #  2b. TypeError: 'classname' object does not support the asynchronous context manager protocol
    #  2c. TypeError: 'classname' object is not subscriptable
    #  2d. TypeError: 'classname' object is not callable
    #  3a. TypeError: 'operator' not supported between instances of 'ClassA' and 'ClassB'
    #  4a. TypeError: byte indices must be integers or slices, not str
    #  5a. TypeError: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`
    #  6a. TypeError: object of type 'classname' has no len()
    #  7a. TypeError: Class must be a sequence. For dicts or sets, use sorted(d).

    if ("missing" in error_message and "required positional argument" in error_message) or \
            ("got an unexpected keyword argument" in error_message) or \
            ("takes no arguments" in error_message):
        element = error_message.split(" ")[1]
        if element.endswith("()"):
            element = element[:-2]
        return element
    return None


def find_member_name_from_attribute_error(error_message: str):
    # 1a. AttributeError: module 'foo' has no attribute 'bar'
    # 2a. AttributeError: 'class' object has no attribute 'foo'

    pattern = r"module\s'(\w+)'[\s\S]*'(\w+)'"
    match = re.search(pattern, error_message)
    if match:
        return match.group(2)

    return error_message.split("'")[1]