"""A tiny entrypoint to run repository helpers under the repo venv.

Use this with the VS Code "Debug runner" configuration to call functions
in `repo_stats.utils` while debugging (breakpoints will be hit).
"""

from __future__ import annotations

import argparse

from repo_stats.utils import count_python_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug runner for repo_stats")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to count Python files under (default: current dir)",
    )
    args = parser.parse_args()
    n = count_python_files(args.path)
    print(f"Python files under {args.path}: {n}")


if __name__ == "__main__":
    main()
