from libmig_test.code_analysis.dummy_code_resources import *
from libmig.code_analysis.qualified_name_index import QualifiedNameIndex


def test_qualified_name_index(qnames_code: str):
    # test for the function get_qname
    qn_index = QualifiedNameIndex(qnames_code)
    assert qn_index.get_qname_at(1) == "func1"
    assert qn_index.get_qname_at(2) is None
    assert qn_index.get_qname_at(3) is None
    assert qn_index.get_qname_at(4) is None
    assert qn_index.get_qname_at(5) == "ClassA"
    assert qn_index.get_qname_at(6) == "ClassA.func1"
    assert qn_index.get_qname_at(7) == "ClassA.func1.ClassA"
    assert qn_index.get_qname_at(8) is None
    assert qn_index.get_qname_at(9) is None
    assert qn_index.get_qname_at(10) is None
    assert qn_index.get_qname_at(11) == "ClassA.func2"
    assert qn_index.get_qname_at(12) == "ClassA.func2.func1"
    assert qn_index.get_qname_at(13) is None
    assert qn_index.get_qname_at(14) is None
    assert qn_index.get_qname_at(15) is None
    assert qn_index.get_qname_at(16) == "ClassB"
    assert qn_index.get_qname_at(17) == "ClassB.ClassA"
    assert qn_index.get_qname_at(18) is None
    assert qn_index.get_qname_at(19) is None
    assert qn_index.get_qname_at(20) is None
    assert qn_index.get_qname_at(21) == "func2"
    assert qn_index.get_qname_at(22) == "func2.func21"
    assert qn_index.get_qname_at(23) is None
