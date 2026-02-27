from dataclasses import dataclass

import libcst as cst

from libmig.code_analysis.qualified_name_index import QualifiedNameIndex


@dataclass(frozen=True, eq=True)
class CSTMapping:
    file: str
    qualified_name: str
    node_before: cst.CSTNode
    node_after: cst.CSTNode


class CSTMapper:
    def __init__(self, file: str, index_before: QualifiedNameIndex, index_after: QualifiedNameIndex):
        self.file = file
        self.index_before = index_before
        self.index_after = index_after
        self.mappings: list[CSTMapping] = []
        self._map()

    def _map(self):
        index_before = self.index_before
        index_after = self.index_after
        mappings = []
        for node_before in index_before.all_nodes:
            node_before: cst.FunctionDef
            qname = index_before.get_qname(node_before)
            node_after = index_after.get_node_by_qname(qname)
            mappings.append(CSTMapping(self.file, qname, node_before, node_after))

        self.mappings = mappings

    def asynced_functions(self):
        return [m for m in self.mappings if _is_asynced(m)]

    def unmapped_mappings(self):
        return [m for m in self.mappings if m.node_after is None]


def _is_asynced(mapping: CSTMapping):
    before = mapping.node_before
    after = mapping.node_after
    if before is None:
        return False
    if after is None:
        return False
    if not isinstance(before, cst.FunctionDef):
        return False
    if not isinstance(after, cst.FunctionDef):
        return False
    if before.asynchronous is not None:
        # old function was already async
        return False
    if after.asynchronous is None:
        # new function is not async
        return False

    return after.asynchronous is not None
