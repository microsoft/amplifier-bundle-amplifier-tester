"""SCRATCH ONLY -- a deliberate ruff F821 (undefined name), to prove the lint job bites."""

def broken() -> int:
    return this_name_is_not_defined_anywhere
