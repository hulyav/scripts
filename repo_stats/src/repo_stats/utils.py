"""Small utilities for repository statistics."""

from pathlib import Path
from typing import Union


def count_python_files(path: Union[str, Path]) -> int:
    """Count .py files under `path` recursively.

    Args:
        path: directory path to search.

    Returns:
        Number of files ending with .py
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    if p.is_file():
        return 1 if p.suffix == ".py" else 0
    return sum(1 for _ in p.rglob("*.py"))
