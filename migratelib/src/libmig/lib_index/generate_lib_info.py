"""
This script is meant to be run on a separate virtual environment.
Therefore, it should only depend on system packages.
This should not depend on any other part of the project as well.
"""
import inspect
import json
import sys
from importlib import import_module
from inspect import *
from pathlib import Path


def get_explicit_doc(member):
    """
    This mimics the behavior of inspect.getdoc but only return the docstring explicitly defined for the member
    :param member:
    :return:
    """
    try:
        doc = member.__doc__
    except AttributeError:
        return ""

    if not isinstance(doc, str):
        return ""

    return cleandoc(doc)


def build_member_info(root_module_path: Path, member):
    sign = inspect.signature(member)

    doc = get_explicit_doc(member)

    abs_source_path = Path(getsourcefile(member))
    file = abs_source_path.relative_to(root_module_path).as_posix()
    _, lineno = getsourcelines(member)

    return {
        "short_name": member.__name__,
        "qualified_name": member.__qualname__,
        "signature": str(sign),
        "type": str(type(member)),
        "file": file,
        "line": lineno,
        "doc": doc
    }


def get_all_recursive(root_module_path: Path, object: object, results: set, depth=0):
    def filter(member):
        try:
            name = member.__name__
            if name.startswith("__"):
                return False

            qname = member.__qualname__
            qname_parts = qname.split(".")
            if any(part[0] == "_" for part in qname_parts):
                return False

            getsourcelines(member)  # check if the member has source code
            file = getsourcefile(member)
            if Path(file).is_relative_to(root_module_path):  # check if the member is part of the library
                return True
        except:
            pass

        return False

    try:
        members = getmembers(object, filter)
    except Exception as e:
        print(f"Failed to get members of {object}: {e}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        return

    all_members = {m[1] for m in members}
    new_members = all_members - results

    results.update(new_members)

    count = len(new_members)
    if not count:
        return

    print(f"{' ' * depth} {object} has {count} new members")
    for i, m in enumerate(new_members, start=1):
        print(f"{' ' * (depth * 2)} {i}/{count} processing {m.__qualname__}")
        get_all_recursive(root_module_path, m, results, depth + 1)


def get_root_module_members(root_module):
    members = set()
    root_module_path = Path(getsourcefile(root_module)).parent
    get_all_recursive(root_module_path, root_module, members)
    for m in members:
        try:
            yield build_member_info(root_module_path, m)
        except (ValueError, TypeError) as e:
            allowed_error_message_parts = [
                "is not supported by signature",
                "no signature found for builtin type",  # excluding built-in types
                "is not a callable object",
                "unexpected object ",
            ]
            error_msg = str(e)
            if any(part in error_msg for part in allowed_error_message_parts):
                pass
            else:
                raise e


def is_code_module(module):
    """Sometimes there are .pyd modules which do not have source code. We want to ignore them."""
    path = getsourcefile(module)
    return path is not None


def generate_lib_info(import_names_csv: str, json_file: Path):
    print(f"Generating lib info for {import_names_csv}")
    import_names = import_names_csv.split(",")

    apis = []
    for name in import_names:
        try:
            root_module = import_module(name)
        except ModuleNotFoundError as e:
            print(f"  {e}")
            print(f"  The above error occurred when trying to generate lib info for import name {name}")
            continue

        if not is_code_module(root_module):
            continue

        apis += list(get_root_module_members(root_module))

    unique_apis = []
    unique_ids = set()
    for api in apis:
        id = f"{api['qualified_name']}@{api['file']}:{api['line']}"
        if id not in unique_ids:
            unique_ids.add(id)
            unique_apis.append(api)

    lib_info = {
        "import_names": import_names,
        "apis": apis
    }

    json_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(lib_info, indent=2), "utf-8")
    print(f"Generated lib info for {import_names_csv}. Written to {json_file}")


if __name__ == '__main__':
    ins = sys.argv[1]
    jfp = Path(sys.argv[2])

    generate_lib_info(ins, jfp)
