from dataclasses import dataclass


def function_id(qalified_name: str, file: str, owner: str):
    return f"{qalified_name}@{file}@{owner}"


def parse_function_id(id: str):
    name, file_line, owner = id.split('@')
    file, line = file_line.split(':')
    return name, file, int(line), owner


@dataclass
class CGFunction:
    owner: str
    """Either "client" or a library name"""
    file: str
    line: int
    name: str
    qualified_name: str
    """Qualified name within a file"""

    def __post_init__(self):
        self.id = function_id(self.qualified_name, self.file, self.owner)
        self.direct_calls_to_me: set[CGCall] = set()
        self.direct_calls_from_me: set[CGCall] = set()

        self.direct_callers = set()
        self.direct_callees = set()
        self.transitive_callers = set()
        self.transitive_callees = set()
        self._all_callers = None
        self._all_callees = None

    @property
    def all_callers(self) -> set['CGFunction']:
        if self._all_callers is None:
            self._all_callers = self.direct_callers | self.transitive_callers
        return self._all_callers

    @property
    def all_callees(self) -> set['CGFunction']:
        if self._all_callees is None:
            self._all_callees = self.direct_callees | self.transitive_callees

        return self._all_callees

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, CGFunction):
            return False
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.id


class CGCall:
    def __init__(self, caller: CGFunction, callee: CGFunction, call_line: int = None):
        self.caller = caller
        self.callee = callee
        self.call_line = call_line

        self.__hash_props = (self.caller, self.callee, self.call_line)

    def __hash__(self):
        return hash(self.__hash_props)

    def __eq__(self, other):
        if not isinstance(other, CGCall):
            return False
        return self.__hash_props == other.__hash_props

    def __str__(self):
        return f"{self.caller.name}->{self.callee.name}"

    def __repr__(self):
        return f"{self.caller.id}->{self.callee.id}@{self.call_line}"


class CG:

    def __init__(self):
        self.direct_calls: set[CGCall] = set()
        self.transitive_calls: set[CGCall] = set()
        self.functions: set[CGFunction] = set()
        self._function_index: dict[str, CGFunction] = {}

    @property
    def all_calls(self):
        # optimize by storing all calls
        return self.direct_calls | self.transitive_calls

    def add_function(self, owner: str, file: str, line: int, name: str, qualified_name: str) -> 'CGFunction':
        id = function_id(qualified_name, file, owner)
        if id not in self._function_index:
            self._function_index[id] = CGFunction(owner, file, line, name, qualified_name)
            self.functions.add(self._function_index[id])

        return self._function_index[id]

    def add_direct_call(self, caller: CGFunction, callee: CGFunction, call_line: int):
        call = CGCall(caller, callee, call_line)
        caller.direct_calls_from_me.add(call)
        callee.direct_calls_to_me.add(call)
        caller.direct_callees.add(callee)
        callee.direct_callers.add(caller)

        self.direct_calls.add(call)

    def add_transitive_call(self, caller: CGFunction, callee: CGFunction):
        call = CGCall(caller, callee)
        self.transitive_calls.add(call)
        caller.transitive_callees.add(callee)
        callee.transitive_callers.add(caller)
