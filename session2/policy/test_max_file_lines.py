import warnings
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    env_int,
    iter_backend_app_python_files,
)

def test_backend_app_files_do_not_exceed_max_lines() -> None:
    """
    Repo policy: keep Python modules small enough to review.

    Default behavior: report violations as a warning (non-failing) so we can
    inspect the current situation.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_MAX_FILE_LINES=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_MAX_FILE_LINES")
    max_lines = env_int("QUEAST_POLICY_MAX_FILE_LINES", default=1000)

    candidates = list(iter_backend_app_python_files(include_tests=True))
    assert candidates, f"No Python files found under {backend_dir() / 'app'}"

    violations: list[tuple[Path, int]] = []
    for path in candidates:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            line_count = sum(1 for _ in handle)
        if line_count > max_lines:
            violations.append((path, line_count))

    if not violations:
        return

    violations.sort(key=lambda item: item[1], reverse=True)
    details = "\n".join(f"- {p.relative_to(backend_dir())}: {count}" for p, count in violations)
    message = (
        f"{len(violations)} file(s) exceed {max_lines} lines under {backend_dir() / 'app'}.\n"
        f"Set QUEAST_POLICY_ENFORCE_MAX_FILE_LINES=1 to hard-fail.\n"
        f"Set QUEAST_POLICY_MAX_FILE_LINES to tune the threshold.\n\n"
        f"{details}"
    )

    if enforce:
        raise AssertionError(message)

    warnings.warn(message, category=UserWarning, stacklevel=1)
