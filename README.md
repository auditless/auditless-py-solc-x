# py-solc-x wrapper for Auditless

This wrapper modifies `py-solcx-x` to produce output on every compilation so that it can be consumed by Auditless.

## Can I use this for my project

As long as you are using `py-solc-x` to compile Solidity files, you can use this wrapper.

## How to use

Add the the following snippet to your code:

```python
from pathlib import Path
from auditless_solcx import solcx_start_saving_debugging_output_to_path

path = Path(__file__).parent  # This will save files in a folder ./artifacts/build-info

solcx_start_saving_debugging_output_to_path(path)
# This needs to appear before any modules consuming `py-solc-x` are loaded
# See below "Important note about patching"
```

## Important note about patching

The patching function `solcx_start_saving_debugging_output_to_path(<path>)` needs to be called either before
`solcx` is used directly or before any module that imports and uses `solcx`.

See [Python Mock Gotchas](https://alexmarandon.com/articles/python_mock_gotchas/) for more information about patching
order.

## License

MIT
