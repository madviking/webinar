import os
import warnings
from pathlib import Path
from typing import Iterable


def backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def app_dir() -> Path:
    return backend_dir() / "app"


def is_excluded_path(path: Path) -> bool:
    path_str = path.as_posix()
    excluded_substrings = [
        "/migrations/",
        "/alembic/",
        "/generated/",
        "/__pycache__/",
    ]
    return any(part in path_str for part in excluded_substrings)


def is_under_tests_dir(path: Path) -> bool:
    return "/tests/" in path.as_posix()


def iter_backend_app_python_files(*, include_tests: bool = True) -> Iterable[Path]:
    base = app_dir()
    for path in sorted(base.rglob("*.py")):
        if is_excluded_path(path):
            continue
        if not include_tests and is_under_tests_dir(path):
            continue
        yield path


def env_flag(name: str, *, default: str = "0") -> bool:
    return os.getenv(name, default) == "1"


def env_int(name: str, *, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw)


def enforce_or_warn(*, enforce: bool, message: str) -> None:
    if enforce:
        raise AssertionError(message)
    warnings.warn(message, category=UserWarning, stacklevel=1)

