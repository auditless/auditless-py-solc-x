"""py-solcx wrapper for use by Auditless."""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import os
import shutil
import subprocess
import json
import secrets
from semantic_version import Version  # type: ignore

import solcx  # type: ignore


class AuditlessSolcxException(Exception):
    """Auditless py-solc-x wrapper exception."""

    pass


def _determine_solidity_version(
    solc_binary: Union[str, Path] = None,
    solc_version: Version = None,
) -> Version:
    """Determine Solidity version."""
    if solc_version is None:
        if solc_binary is None:
            solc_binary = solcx.main.get_executable(solc_version)
        solc_version = solcx.wrapper._get_solc_version(solc_binary)
    return solc_version


def _resolve_urls(input_data: Dict) -> Dict:
    """Replace file locations with contents in urls."""
    for filename in input_data["sources"]:
        fileobj = input_data["sources"][filename]
        if "urls" in fileobj:
            last_url = fileobj["urls"][-1]
            if "ipfs://" in last_url or "bzzr:" in last_url:
                raise AuditlessSolcxException(f"We do not currently support remote file compilation in url={last_url}.")
            content = None
            with open(last_url, "r") as f:
                content = f.read()
            if content is None:
                raise AuditlessSolcxException(f"Could not read file contents at url={last_url}.")
            input_data["sources"][filename] = dict(content=content)
    return input_data


def _extract_combined_json_from_compile_standard(input_data: Dict, base_path: str = None) -> Dict:
    """Normalize json input file to include files."""
    input_data = _resolve_urls(input_data)

    if base_path is not None:
        raise AuditlessSolcxException(f"Base path has been provided for contracts. We do not currently support contract urls. Please contact us if you need this capability.")
    # TODO: Remap paths based on base path

    # It's worth noting that at this stage we do not remap any input/output arguments
    # Hardhat would normally store additional information in these files by remapping the inputs
    # and providing room for the outputs. In this case, we exclude the outputs and only
    # include input settings which the back-end will partially override

    return input_data


def _save_artifacts(
    output_directory: Path, standard_json: Dict[str, Any], solc_version: str
) -> None:
    """Store artifacts in a new .json file within output directory."""
    build_info = dict(_format="hh-sol-build-info-1", solcVersion=solc_version, input=standard_json)
    name = secrets.token_hex(nbytes=16) + ".json"
    with open(output_directory / name, "w") as f:
        json.dump(build_info, f, indent=2)


def create_compile_standard(output_directory: Path):
    """Wrapped compile_standard function."""

    def compile_standard(
        input_data: Dict,
        base_path: str = None,
        allow_paths: List = None,
        output_dir: str = None,
        overwrite: bool = False,
        solc_binary: Union[str, Path] = None,
        solc_version: Version = None,
        allow_empty: bool = False,
    ) -> Dict:
        input_data = _extract_combined_json_from_compile_standard(input_data, base_path)

        solc_version = _determine_solidity_version(solc_binary, solc_version)

        _save_artifacts(output_directory, input_data, str(solc_version))

        return solcx.main.compile_standard(
            input_data,
            base_path,
            allow_paths,
            output_dir,
            overwrite,
            solc_binary,
            solc_version,
            allow_empty,
        )

    return compile_standard


def create_compile_files(output_directory: Path):
    """Wrapped compile_files function."""

    def compile_files(
        source_files: Union[List, Path, str],
        output_values: List = None,
        import_remappings: Union[Dict, List, str] = None,
        base_path: Union[Path, str] = None,
        allow_paths: Union[List, Path, str] = None,
        output_dir: Union[Path, str] = None,
        overwrite: bool = False,
        evm_version: str = None,
        revert_strings: Union[List, str] = None,
        metadata_hash: str = None,
        metadata_literal: bool = False,
        optimize: bool = False,
        optimize_runs: int = None,
        optimize_yul: bool = False,
        no_optimize_yul: bool = False,
        yul_optimizations: int = None,
        solc_binary: Union[str, Path] = None,
        solc_version: Version = None,
        allow_empty: bool = False,
    ) -> Dict:
        
        _compile_combined_json(
            output_directory=output_directory,

            solc_binary=solc_binary,
            solc_version=solc_version,
            source_files=source_files,
            output_values=output_values,
            import_remappings=import_remappings,
            base_path=base_path,
            allow_paths=allow_paths,
            output_dir=output_dir,
            overwrite=overwrite,
            evm_version=evm_version,
            revert_strings=revert_strings,
            metadata_hash=metadata_hash,
            metadata_literal=metadata_literal,
            optimize=optimize,
            optimize_runs=optimize_runs,
            no_optimize_yul=no_optimize_yul,
            yul_optimizations=yul_optimizations,
            allow_empty=allow_empty,
        )

        return solcx.main.compile_files(
            source_files,
            output_values,
            import_remappings,
            base_path,
            allow_paths,
            output_dir,
            overwrite,
            evm_version,
            revert_strings,
            metadata_hash,
            metadata_literal,
            optimize,
            optimize_runs,
            optimize_yul,
            no_optimize_yul,
            yul_optimizations,
            solc_binary,
            solc_version,
            allow_empty
        )

    return compile_files


def create_compile_source(output_directory: Path):
    """Wrapped compile_source function."""

    def compile_source(
        source: str,
        output_values: List = None,
        import_remappings: Union[Dict, List, str] = None,
        base_path: Union[Path, str] = None,
        allow_paths: Union[List, Path, str] = None,
        output_dir: Union[Path, str] = None,
        overwrite: bool = False,
        evm_version: str = None,
        revert_strings: Union[List, str] = None,
        metadata_hash: str = None,
        metadata_literal: bool = False,
        optimize: bool = False,
        optimize_runs: int = None,
        optimize_yul: bool = False,
        no_optimize_yul: bool = False,
        yul_optimizations: int = None,
        solc_binary: Union[str, Path] = None,
        solc_version: Version = None,
        allow_empty: bool = False,
    ) -> Dict:
        _compile_combined_json(
            output_directory=output_directory,

            solc_binary=solc_binary,
            solc_version=solc_version,
            stdin=source,
            output_values=output_values,
            import_remappings=import_remappings,
            base_path=base_path,
            allow_paths=allow_paths,
            output_dir=output_dir,
            overwrite=overwrite,
            evm_version=evm_version,
            revert_strings=revert_strings,
            metadata_hash=metadata_hash,
            metadata_literal=metadata_literal,
            optimize=optimize,
            optimize_runs=optimize_runs,
            no_optimize_yul=no_optimize_yul,
            yul_optimizations=yul_optimizations,
            allow_empty=allow_empty,
        )

        return solcx.main.compile_source(
            source,
            output_values,
            import_remappings,
            base_path,
            allow_paths,
            output_dir,
            overwrite,
            evm_version,
            revert_strings,
            metadata_hash,
            metadata_literal,
            optimize,
            optimize_runs,
            optimize_yul,
            no_optimize_yul,
            yul_optimizations,
            solc_binary,
            solc_version,
            allow_empty
        )

    return compile_source


def _normalize_solidity_input(name: str, solidity_input: Union[str, Path, List, Dict, None]) -> List[str]:
    """Normalize a Solidity input into generic format."""
    if isinstance(solidity_input, dict):
        return {name: [f"{k}={v}" for k, v in solidity_input.iter()]}
    elif isinstance(solidity_input, list):
        return {name: list(map(str, solidity_input))}
    elif solidity_input is not None:
        return {name: str(solidity_input)}
    return {}


def _filename(path: Union[str, Path]) -> str:
    """Get filename and extension from the full path."""
    if isinstance(path, str):
        return Path(path).name
    return path.name


def extract_combined_json_from_compile_combined_json(
    # Arguments of the original function
    output_values: Optional[List],
    solc_binary: Union[str, Path, None],
    solc_version: Optional[Version],
    output_dir: Union[str, Path, None],
    overwrite: Optional[bool],
    allow_empty: Optional[bool],

    # Solidity arguments

    # Compile files arguments
    source_files: Union[List, Path, str, None] = None,
    import_remappings: Union[Dict, List, str] = None,
    base_path: Union[Path, str] = None,
    allow_paths: Union[List, Path, str] = None,
    evm_version: str = None,
    revert_strings: Union[List, str] = None,
    metadata_hash: str = None,
    metadata_literal: bool = False,
    optimize: bool = False,
    optimize_runs: int = None,
    optimize_yul: bool = False,
    no_optimize_yul: bool = False,
    yul_optimizations: int = None,

    # Compile source arguments
    stdin: Union[str, None] = None,  # Used for file source conventionally
) -> Dict:
    """Normalize json input file from cli arguments to standard json."""

    if isinstance(source_files, List):
        sources = {_filename(path): dict(urls=[path]) for path in source_files}
    elif source_files is not None:
        source_files = str(source_files)
        sources = {_filename(source_files): dict(urls=[source_files])}
    elif stdin is not None:
        sources = {"<stdin>": dict(content=stdin)}
    else:
        raise AuditlessSolcxException(f"No source files specified when calling _compile_combined_json.")
    
    metadata = dict()
    if metadata_hash is not None:
        if "metadata" not in metadata:
            metadata["metadata"] = dict()
        metadata["metadata"]["bytecodeHash"] = metadata_hash
    if metadata_literal:
        if "metadata" not in metadata:
            metadata["metadata"] = dict()
        metadata["metadata"]["useLiteralContent"] = metadata_literal
    
    optimizer = dict()
    if optimize:
        if "optimizer" not in optimizer:
            optimizer["optimizer"] = dict()
        optimizer["optimizer"]["enabled"] = True
    if optimize_runs is not None:
        if "optimizer" not in optimizer:
            optimizer["optimizer"] = dict()
        optimizer["optimizer"]["runs"] = optimize_runs
    if optimize_yul:
        if "optimizer" not in optimizer:
            optimizer["optimizer"] = dict()
        if "details" not in optimizer["optimizer"]:
            optimizer["optimizer"]["details"] = dict()
        optimizer["optimizer"]["details"]["yul"] = True
    if yul_optimizations is not None:
        raise AuditlessSolcxException("YUL optimization is not currently supported.")

    input_data = dict(
        language="Solidity",
        sources=sources,
        settings={
            **_normalize_solidity_input("remappings", import_remappings),
            **_normalize_solidity_input("evmVersion", evm_version),
            **({} if revert_strings is None else dict(debug=dict(revertStrings=revert_strings))),
            **metadata,
            **optimizer
        }
    )

    input_data = _resolve_urls(input_data)

    if base_path is not None:
        raise AuditlessSolcxException(f"Base path has been provided for contracts. We do not currently support contract urls. Please contact us if you need this capability.")
    # TODO: Remap paths based on base path

    # It's worth noting that at this stage we do not remap any input/output arguments
    # Hardhat would normally store additional information in these files by remapping the inputs
    # and providing room for the outputs. In this case, we exclude the outputs and only
    # include input settings which the back-end will partially override

    return input_data


def _compile_combined_json(
    # Wrapper argument
    output_directory: str,

    # Arguments of the original function
    output_values: Optional[List],
    solc_binary: Union[str, Path, None],
    solc_version: Optional[Version],
    output_dir: Union[str, Path, None],
    overwrite: Optional[bool],
    allow_empty: Optional[bool],

    # Solidity arguments

    # Compile files arguments
    source_files: Union[List, Path, str] = None,
    import_remappings: Union[Dict, List, str] = None,
    base_path: Union[Path, str] = None,
    allow_paths: Union[List, Path, str] = None,
    evm_version: str = None,
    revert_strings: Union[List, str] = None,
    metadata_hash: str = None,
    metadata_literal: bool = False,
    optimize: bool = False,
    optimize_runs: int = None,
    optimize_yul: bool = False,
    no_optimize_yul: bool = False,
    yul_optimizations: int = None,

    # Compile source arguments
    stdin: str = None,  # Used for file source conventionally

    **kwargs: Any,
) -> Dict:
    """Helper function for wrapping compile_source and compile_files."""
    if kwargs:
        raise AuditlessSolcxException(f"Unsupported arguments when running _create_combined_json {kwargs}. Are you using a new solc version?")

    input_data = extract_combined_json_from_compile_combined_json(
        output_values,
        solc_binary,
        solc_version,
        output_dir,
        overwrite,
        allow_empty,

        source_files,
        import_remappings,
        base_path,
        allow_paths,
        evm_version,
        revert_strings,
        metadata_hash,
        metadata_literal,
        optimize,
        optimize_runs,
        optimize_yul,
        no_optimize_yul,
        yul_optimizations,

        stdin,
    )

    solc_version = _determine_solidity_version(solc_binary, solc_version)

    _save_artifacts(output_directory, input_data, str(solc_version))


def solcx_start_saving_debugging_output_to_path(project_root: Union[str, Path]) -> None:
    """Emit solcx debug output from compilations to a directory.
    This clears the directory on every run.

    Arguments
    ---------
    project_root : Union[str, Path]
        Root directory of the project. All json files will be stored in the format
        <project_root>/artifacts/build-info/*.json
    """

    output_directory = None
    if isinstance(project_root, Path):
        output_directory = project_root / "artifacts" / "build-info"
    else:
        output_directory = Path(project_root) / "artifacts" / "build-info"

    # Find the directory
    try:
        output_directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise AuditlessSolcxException(
            f"Could not create/find directory at provided path output_directory={output_directory}. reason={str(e)}"
        )

    # Clear the directory from any existing files
    for filename in os.listdir(output_directory):
        file_path = output_directory / filename
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            raise AuditlessSolcxException(
                f"Could not remove all files in output_directory={output_directory}, reason={str(e)}"
            )

    # Check that py-solc-x design hasn't changed
    try:
        from solcx.main import compile_standard  # type: ignore
    except ImportError:
        raise AuditlessSolcxException(
            "Cannot find compile_standard function in solcx, please update auditless-py-solc-x"
        )

    # Monkey patch solcx internally
    old_compile_standard = solcx.compile_standard
    solcx.compile_standard = create_compile_standard(output_directory)
    solcx.compile_standard.__doc__ = old_compile_standard.__doc__

    old_compile_files = solcx.compile_files
    solcx.compile_files = create_compile_files(output_directory)
    solcx.compile_files.__doc__ = old_compile_files.__doc__

    old_compile_source = solcx.compile_source
    solcx.compile_source = create_compile_source(output_directory)
    solcx.compile_source.__doc__ = old_compile_source.__doc__


__all__ = ["solcx_start_saving_debugging_output_to_path", "AuditlessSolcxException", "extract_combined_json_from_compile_combined_json"]
