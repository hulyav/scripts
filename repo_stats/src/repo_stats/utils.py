"""Small utilities for repository statistics."""

import json
import subprocess
from pathlib import Path

import ijson


def collect_commit_stats(repo_path: str, out_json: str | Path) -> int:
    """Collect commit metadata from a local git repository and write to JSON.

    Args:
        repo_path: Path to the git repository.
        out_json: Output JSON file path.

    Returns:
        List of commit dicts written to the file.

    The function uses an unambiguous record and field separator so commit
    messages and author names are parsed reliably.
    """
    repo = Path(repo_path)
    if not (repo / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_path}")

    # Use ASCII unit separator and record separator to make parsing robust
    # include committer info and both author and commit dates/timestamps
    # fields: hash, author_name, author_email, author_date, author_ts,
    # committer_name, committer_email, commit_date, commit_ts, message
    fmt = "%H%x1f%an%x1f%ae%x1f%ad%x1f%at%x1f%cn%x1f%ce%x1f%cd%x1f%ct%x1f%B%x1e"

    rev_cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        "--all",
        f"--pretty=format:{fmt}",
        "--date=short",
    ]

    proc = subprocess.Popen(
        rev_cmd, stdout=subprocess.PIPE, text=True, errors="replace"
    )
    out_path = Path(out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    first = True
    count = 1

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("[")
        if proc.stdout is None:
            proc.wait()
            fh.write("]")
            return 0

        buffer = ""
        while True:
            chunk = proc.stdout.read(4096)  # read in chunks
            if not chunk:
                break  # end of stream
            buffer += chunk

            while "\x1e" in buffer:
                record, buffer = buffer.split("\x1e", 1)
                record = record.strip()
                if not record:
                    continue
                parts = record.split("\x1f")
                if len(parts) < 9:
                    continue
                (
                    commit_hash,
                    author_name,
                    author_email,
                    author_date_str,
                    author_ts_str,
                    committer_name,
                    committer_email,
                    commit_date_str,
                    commit_ts_str,
                ) = parts[:9]
                # some commits lack a message; those cannot be covered
                # with the code above
                if len(parts) > 9:
                    message = parts[9]
                else:
                    message = ""

                try:
                    author_date = author_date_str
                    author_timestamp = int(author_ts_str)
                except Exception:
                    author_date = author_date_str
                    author_timestamp = None
                try:
                    commit_date = commit_date_str
                    commit_timestamp = int(commit_ts_str)
                except Exception:
                    commit_date = commit_date_str
                    commit_timestamp = None

                obj = {
                    "count": count,
                    "hash": commit_hash,
                    "author_name": author_name,
                    "author_email": author_email,
                    "author_date": author_date,
                    "author_timestamp": author_timestamp,
                    "committer_name": committer_name,
                    "committer_email": committer_email,
                    "commit_date": commit_date,
                    "commit_timestamp": commit_timestamp,
                    "has_heatwave": ("heatwave" in (message or "").lower()),
                    "message": message,
                }

                if not first:
                    fh.write(",\n")
                fh.write(json.dumps(obj, ensure_ascii=False))

                first = False
                count += 1

        proc.wait()
        fh.write("]")
    return count


def read_commit_slice(json_path: str, start: int, stop: int) -> list[dict]:
    """
    Reads commit objects from a large JSON file between indices [start, stop).
    """
    results = []
    with open(json_path, "rb") as f:
        parser = ijson.items(f, "item")
        for idx, item in enumerate(parser):
            if idx < start:
                continue
            if idx > stop:
                break
            results.append(item)
    return results


def collect_commit_file_stats(
    in_json: str | Path,
    start: int,
    stop: int,
    repo_path: str,
    out_json: str | Path,
    files_start_count: int = 0,
) -> int:
    """
    Collect file-change statistics for commits in the given range.

    Reads commits from a large JSON file and writes per-commit file stats
    and a summary JSON file.
    """
    repo = Path(repo_path)
    if not (repo / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_path}")

    commits = read_commit_slice(in_json, start, stop)

    out_path = Path(out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # summary file should live alongside the per-file output
    out_path_sum = out_path.parent / f"summary_{out_path.name}"
    out_path_sum.parent.mkdir(parents=True, exist_ok=True)

    first = True
    count = files_start_count + 1
    first_sum = True
    with out_path_sum.open("w", encoding="utf-8") as fh_sum:
        fh_sum.write("[")
        with out_path.open("w", encoding="utf-8") as fh:
            fh.write("[")

            for commit in commits:
                print(commit["count"], count)
                try:
                    commit_hash = commit["hash"]
                    files_out = subprocess.check_output(
                        [
                            "git",
                            "-C",
                            str(repo),
                            "show",
                            "--numstat",
                            "--format=",
                            commit_hash,
                        ],
                        text=True,
                        errors="replace",
                    )
                    insertions = 0
                    deletions = 0
                    file = ""
                    insertions_count = 0
                    deletions_count = 0
                    insertions_count_exc = 0
                    deletions_count_exc = 0
                    files_count = 0
                    for line in files_out.splitlines():
                        if line.strip() == "":
                            continue
                        divs = line.split("\t")
                        if len(divs) < 3:
                            print("hash: skipped line: ", commit["hash"], line)
                            continue
                        (
                            insertions,
                            deletions,
                            file,
                        ) = divs[:3]
                        obj = {
                            "count": count,
                            "hash": commit_hash,
                            "insertions": insertions,
                            "deletions": deletions,
                            "file": file,
                        }
                        if insertions.isdigit():
                            insertions_int = int(insertions)
                        else:
                            insertions_int = 0

                        if deletions.isdigit():
                            deletions_int = int(deletions)
                        else:
                            deletions_int = 0
                        insertions_count += insertions_int
                        deletions_count += deletions_int
                        files_count += 1
                        is_extra = file.startswith("extra/") or ("=> extra/" in file)
                        if is_extra:
                            insertions_count_exc += insertions_int
                            deletions_count_exc += deletions_int

                        if not first:
                            fh.write(",\n")
                        fh.write(json.dumps(obj, ensure_ascii=False))
                        first = False
                        count += 1

                    obj = {
                        "hash": commit_hash,
                        "insertions_count": insertions_count,
                        "deletions_count": deletions_count,
                        "insertions_count_exc": (
                            insertions_count - insertions_count_exc
                        ),
                        "deletions_count_exc": (deletions_count - deletions_count_exc),
                        "file": files_count,
                    }

                    if not first_sum:
                        fh_sum.write(",\n")
                    fh_sum.write(json.dumps(obj, ensure_ascii=False))
                    first_sum = False

                except subprocess.CalledProcessError:
                    insertions_count = 0
                    deletions_count = 0
                    insertions_count_exc = 0
                    deletions_count_exc = 0
                    files_count = 0

            fh.write("]")
        fh_sum.write("]")

    return count
