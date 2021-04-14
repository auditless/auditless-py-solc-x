from pathlib import Path
from typing import Dict, List
import json

import pytest
import solcx

from auditless_solcx import (
    solcx_start_saving_debugging_output_to_path,
    AuditlessSolcxException,
    extract_combined_json_from_compile_combined_json,
)
import util


def gather_build_info_files() -> List[Dict]:
    """Gather all json files in artifacts/build-info return as a structured list without filenames."""
    path = Path(__file__).parent.parent / "artifacts" / "build-info"

    json_output = []
    for filepath in path.glob("*.json"):
        with open(filepath, "r") as f:
            file_contents = json.load(f)
            json_output.append(file_contents)

    return json_output


@pytest.fixture
def patched_solcx():
    path = Path(__file__).parent.parent

    # To use auditless_solcx, all you need to do is to trigger the solcx modification
    solcx_start_saving_debugging_output_to_path(path)


def test_compile_standard(patched_solcx):
    # Then continue using the solcx compiler as normal
    std_input = {
        "language": "Solidity",
        "sources": {
            "file1": {
                "content": "pragma solidity ^0.7.6;\ncontract Test { function test() public { } }"
            },
            "file2": {
                "content": 'import "file1";\npragma solidity ^0.7.6;\ncontract Test2 { function test() public { Test test = new Test(); } }'
            },
        },
        "settings": {"outputSelection": {"*": {"*": ["metadata", "evm.bytecode"]}}},
    }

    solcx.set_solc_version("0.7.6")
    solcx.compile_standard(std_input)

    # This library will now generate additional output files
    output_files = gather_build_info_files()
    assert output_files == [
        dict(_format="hh-sol-build-info-1", solcVersion="0.7.6", input=std_input)
    ]


def test_compile_standard_in_submodule(patched_solcx):
    std_input = {
        "language": "Solidity",
        "sources": {
            "file1": {
                "content": "pragma solidity ^0.7.6;\ncontract Test { function test() public { } }"
            },
            "file2": {
                "content": 'import "file1";\npragma solidity ^0.7.6;\ncontract Test2 { function test() public { Test test = new Test(); } }'
            },
        },
        "settings": {"outputSelection": {"*": {"*": ["metadata", "evm.bytecode"]}}},
    }

    solcx.set_solc_version("0.7.6")
    # Run compile_standard in submodule
    util.compile_standard(std_input)

    output_files = gather_build_info_files()
    assert output_files == [
        dict(_format="hh-sol-build-info-1", solcVersion="0.7.6", input=std_input)
    ]


def test_compile_source(patched_solcx):
    solcx.set_solc_version("0.7.6")

    source = "pragma solidity ^0.7.6;\ncontract Test { function test() public { } }"
    solcx.compile_source(source)

    std_input = {
        "language": "Solidity",
        "sources": {
            "<stdin>": {
                "content": source
            },
        },
        "settings": {}
    }

    output_files = gather_build_info_files()
    assert output_files == [
        dict(_format="hh-sol-build-info-1", solcVersion="0.7.6", input=std_input)
    ]


def test_compile_files(patched_solcx):
    solcx.set_solc_version("0.7.6")

    url = str(Path(__file__).parent / "contracts" / "contract.sol")
    solcx.compile_files(url)

    with open(url, "r") as f:
        content = f.read()

    std_input = {
        "language": "Solidity",
        "sources": {
            "contract.sol": {
                "content": content
            },
        },
        "settings": {}
    }

    output_files = gather_build_info_files()
    assert output_files == [
        dict(_format="hh-sol-build-info-1", solcVersion="0.7.6", input=std_input)
    ]
