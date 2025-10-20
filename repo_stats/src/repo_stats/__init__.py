"""repo_stats package

Expose the commonly-used functions from :mod:`repo_stats.utils` at
package import time so callers can do ``from repo_stats import
collect_commit_stats``.
"""

from .utils import collect_commit_file_stats, collect_commit_stats, read_commit_slice

__all__ = [
    "collect_commit_stats",
    "collect_commit_file_stats",
    "read_commit_slice",
]
