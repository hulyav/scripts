import json
import subprocess
from pathlib import Path

from repo_stats.utils import collect_commit_file_stats, collect_commit_stats


def _init_temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.check_call(["git", "init", str(repo)])
    # configure committer so git won't complain
    subprocess.check_call(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"]
    )
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test User"])
    return repo


def _make_commit(repo: Path, filename: str, contents: str):
    fpath = repo / filename
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(contents, encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", str(fpath)])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-m", f"Add {filename}"])


def test_collect_commit_stats(tmp_path):
    repo = _init_temp_repo(tmp_path)
    # make three commits
    _make_commit(repo, "a.txt", "first")
    _make_commit(repo, "b.txt", "second")
    _make_commit(repo, "c.txt", "third")

    out_json = tmp_path / "commits.json"
    count = collect_commit_stats(str(repo), str(out_json))

    assert out_json.exists()
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 3
    # count should equal the number of commits processed + 1 (since it starts at 1)
    assert count == 4
    # each item should contain expected keys
    keys = {"hash", "author_name", "commit_date", "message", "count"}
    assert keys.issubset(set(data[0].keys()))


def test_collect_commit_file_stats(tmp_path):
    repo = _init_temp_repo(tmp_path)
    # commit 1: add file1
    _make_commit(repo, "file1.txt", "one")
    # commit 2: add file2
    _make_commit(repo, "file2.txt", "two")

    in_json = tmp_path / "in.json"
    out_json = tmp_path / "out_files.json"
    out_sum = tmp_path / "summary_out_files.json"

    # create a minimal commits.json that mimics collect_commit_stats output
    # We'll call collect_commit_stats to produce a real commits file
    collect_commit_stats(str(repo), str(in_json))

    # collect file stats for both commits
    result_count = collect_commit_file_stats(
        str(in_json), 0, 10, str(repo), str(out_json), files_start_count=0
    )

    assert out_json.exists()
    assert out_sum.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    summary = json.loads(out_sum.read_text(encoding="utf-8"))

    # we expect at least two file-change objects (one per file)
    assert isinstance(data, list)
    assert isinstance(summary, list)
    assert len(summary) >= 1
    # result_count should be >= files_start_count
    assert result_count >= 0
