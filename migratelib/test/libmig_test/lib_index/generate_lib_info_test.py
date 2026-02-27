import json
from pathlib import Path

from libmig.lib_index.generate_lib_info import generate_lib_info


def test_generate_lib_info__typer():
    out = Path(".lib_index/typer.json")
    generate_lib_info("typer", out)
    assert out.exists()
    info = json.load(open(out))
    out.unlink()

    assert info["import_names"] == ["typer"]
    apis = info["apis"]
    assert len(apis) > 0

    assert any(api["short_name"] == "echo" for api in apis)
    # this fails because echo is imported into typer from click.
    # how do we handle this?


def test_generate_lib_info__httpx():
    out_path = Path(".lib_index/httpx.json")
    generate_lib_info("httpx", out_path)
    assert out_path.exists()
