import re
from pathlib import Path

from backend.tests.policy._utils import app_dir, backend_dir, env_flag, enforce_or_warn, is_excluded_path


_ORM_MARKERS = [
    re.compile(r"\bsqlalchemy\b"),
    # Note: we intentionally do NOT flag `sqlmodel.Session` usage in routers.
    # Passing a DB session into a service/repository can be a pragmatic composition-root
    # choice, and flagging it tends to create low-signal, high-churn warnings.
    #
    # We *do* flag query construction/execution and direct SQL statement shapes.
    re.compile(r"\bfrom\s+sqlmodel\s+import\b.*\bselect\b", re.IGNORECASE),
    re.compile(r"\bselect\("),
    re.compile(r"\.query\("),
    re.compile(r"\.execute\("),
    re.compile(r"\.exec\("),
    # SQL keywords are intentionally scoped to common statement shapes to avoid noisy
    # false positives like FastAPI route paths ("/select-tenant") or decorators
    # ("@router.delete(...)").
    re.compile(r"\bSELECT\b.*\bFROM\b", re.IGNORECASE),
    re.compile(r"\bINSERT\b.*\bINTO\b", re.IGNORECASE),
    re.compile(r"\bUPDATE\b.*\bSET\b", re.IGNORECASE),
    re.compile(r"\bDELETE\b.*\bFROM\b", re.IGNORECASE),
]


def _scan_for_markers(path: Path) -> list[int]:
    hits: list[int] = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if any(rx.search(line) for rx in _ORM_MARKERS):
            hits.append(i)
            if len(hits) >= 5:
                break
    return hits


def test_router_and_service_files_do_not_contain_sql_or_orm_code() -> None:
    """
    Repo policy: routers should not talk to the DB layer directly.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_NO_SQL_OR_ORM_IN_ROUTER_SERVICE=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_NO_SQL_OR_ORM_IN_ROUTER_SERVICE")

    targets = []
    targets.extend(app_dir().rglob("router.py"))

    violations: list[tuple[Path, list[int]]] = []
    for path in sorted(set(targets)):
        if is_excluded_path(path) or "/tests/" in path.as_posix():
            continue
        hit_lines = _scan_for_markers(path)
        if hit_lines:
            violations.append((path, hit_lines))

    if not violations:
        return

    details = "\n".join(
        f"- {p.relative_to(backend_dir())}:{','.join(map(str, lines))}" for p, lines in violations
    )
    message = (
        f"{len(violations)} router file(s) appear to contain SQL/ORM usage under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_NO_SQL_OR_ORM_IN_ROUTER_SERVICE=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)
