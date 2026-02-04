import re
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    enforce_or_warn,
    iter_backend_app_python_files,
)


_HTML_TAG_RE = re.compile(r"<[A-Za-z][^>]*>")


def test_backend_app_python_files_do_not_inline_html() -> None:
    """
    Repo policy: inline HTML should live in template files, not Python strings.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_NO_INLINE_HTML=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_NO_INLINE_HTML")

    violations: list[tuple[Path, int, str]] = []
    for path in iter_backend_app_python_files(include_tests=True):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if _HTML_TAG_RE.search(line):
                violations.append((path, line_number, line.strip()))
                break

    if not violations:
        return

    details = "\n".join(f"- {p.relative_to(backend_dir())}:{line_number}" for p, line_number, _ in violations)
    message = (
        f"{len(violations)} Python file(s) appear to contain inline HTML under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_NO_INLINE_HTML=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)

