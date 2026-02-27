import libcst as cst
from libcst.metadata import PositionProvider


class QualifiedNameIndex():
    def __init__(self, tree_or_code: cst.Module | str):
        self.__visitor = _QNameVisitor()

        self.module = cst.parse_module(tree_or_code) if isinstance(tree_or_code, str) else tree_or_code
        module_wrapper = cst.MetadataWrapper(self.module)
        module_wrapper.visit(self.__visitor)

        self._node_to_qname = self.__visitor.node_qname_map
        self._line_to_qname = self.__visitor.line_qname_map
        self._qname_to_node = {qname: node for node, qname in self._node_to_qname.items()}

        self.all_nodes = list(self._node_to_qname.keys())

    def get_qname(self, node: cst.FunctionDef | cst.ClassDef):
        return self.__visitor.node_qname_map.get(node, None)

    def get_qname_at(self, line: int):
        return self.__visitor.line_qname_map.get(line, None)

    def get_node_by_qname(self, qname: str):
        return self._qname_to_node.get(qname, None)


class _QNameVisitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self):
        super().__init__()
        self._current_name_stack = []
        self.node_qname_map: dict[cst.CSTNode, str] = {}
        self.line_qname_map: dict[int, str] = {}

    def _visit_any_def(self, node: cst.FunctionDef | cst.ClassDef):
        name = node.name.value
        qname = ".".join(self._current_name_stack + [name])
        self.node_qname_map[node] = qname

        position = self.get_metadata(PositionProvider, node)
        self.line_qname_map[position.start.line] = qname

        self._current_name_stack.append(name)

    def _leave_any_def(self, _: cst.FunctionDef | cst.ClassDef):
        self._current_name_stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        self._visit_any_def(node)

    def visit_ClassDef(self, node: cst.ClassDef):
        self._visit_any_def(node)

    def leave_FunctionDef(self, node: cst.FunctionDef):
        self._leave_any_def(node)

    def leave_ClassDef(self, node: cst.ClassDef):
        self._leave_any_def(node)
