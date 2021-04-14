"""Testing utility to test path behavior in different modules."""

from typing import Any, List

import solcx


def compile_standard(*args: List, **kwargs: Any):
    return solcx.compile_standard(*args, **kwargs)