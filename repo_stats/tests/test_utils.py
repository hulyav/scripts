import pytest

from repo_stats.utils import count_python_files


def test_count_python_files(tmp_path):
    # create files
    d = tmp_path / "pkg"
    d.mkdir()
    f1 = d / "a.py"
    f1.write_text("print('a')")
    f2 = d / "b.txt"
    f2.write_text("not python")
    sd = d / "sub"
    sd.mkdir()
    f3 = sd / "c.py"
    f3.write_text("print('c')")

    assert count_python_files(d) == 2


def test_count_python_files_file(tmp_path):
    f = tmp_path / "single.py"
    f.write_text("pass")
    assert count_python_files(f) == 1


def test_count_python_files_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        count_python_files(tmp_path / "nope")
