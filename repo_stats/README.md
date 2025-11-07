Repo Stats
===========

A Python package for collecting and analyzing Git repository statistics.

## Features

- **Collect commit metadata** - Extract commit information (hash, author, date, message) from Git repositories
- **Analyze file changes** - Get detailed file-level statistics (insertions, deletions) for commits

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

## Usage

### 1. Collect Commit Metadata

Use `collect_commit_stats` to extract all commit information from a Git repository and save it to a JSON file.

```python
from repo_stats import collect_commit_stats

# Collect all commits from a repository
repo_path = "/path/to/your/git/repo"
output_file = "commits.json"

count = collect_commit_stats(repo_path, output_file)
print(f"Collected {count} commits")
```

**Output format** (`commits.json`):
```json
[
  {
    "count": 1,
    "hash": "abc123...",
    "author_name": "Jane Doe",
    "author_email": "jane@example.com",
    "author_date": "2024-01-15",
    "author_timestamp": 1705334400,
    "committer_name": "Jane Doe",
    "committer_email": "jane@example.com",
    "commit_date": "2024-01-15",
    "commit_timestamp": 1705334400,
    "has_heatwave": false,
    "message": "Initial commit"
  },
  ...
]
```

### 2. Collect File-Level Statistics

Use `collect_commit_file_stats` to analyze file changes for a range of commits. This requires a commits JSON file (from step 1).

```python
from repo_stats import collect_commit_file_stats

# Analyze file changes for commits 0-100
input_commits = "commits.json"
repo_path = "/path/to/your/git/repo"
output_file = "file_stats.json"

count = collect_commit_file_stats(
    in_json=input_commits,
    start=0,              # Start index (inclusive)
    stop=100,             # Stop index (exclusive)
    repo_path=repo_path,
    out_json=output_file,
    files_start_count=0   # Starting count for output records (default: 0)
)
print(f"Processed {count} file changes")
```

**Outputs two files:**

1. **`file_stats.json`** - Detailed per-file changes:
```json
[
  {
    "count": 1,
    "hash": "abc123...",
    "insertions": "45",
    "deletions": "12",
    "file": "src/main.py"
  },
  ...
]
```

2. **`summary_file_stats.json`** - Summary per commit:
```json
[
  {
    "hash": "abc123...",
    "insertions_count": 100,
    "deletions_count": 25,
    "insertions_count_exc": 90,
    "deletions_count_exc": 20,
    "file": 5
  },
  ...
]
```

### Processing Large Repositories

For large repositories, process commits in batches:

```python
from repo_stats import collect_commit_stats, collect_commit_file_stats

# Step 1: Collect all commits once
collect_commit_stats("/path/to/repo", "all_commits.json")

# Step 2: Process in batches of 1000 commits
batch_size = 1000
file_count = 0

for batch_num in range(0, 10):  # Process 10 batches
    start = batch_num * batch_size
    stop = start + batch_size
    
    file_count = collect_commit_file_stats(
        in_json="all_commits.json",
        start=start,
        stop=stop,
        repo_path="/path/to/repo",
        out_json=f"batch_{batch_num}_files.json",
        files_start_count=file_count
    )
```

## Development

Common make targets:

- `make venv` - create `.venv`
- `make install` - install dev requirements
- `make test` - run pytest
- `make lint` - run flake8
- `make format` - run black and isort

## Testing

```bash
# Run all tests
make test

# Or use pytest directly
pytest -q repo_stats/tests
```
