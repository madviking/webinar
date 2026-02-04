import ast
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    enforce_or_warn,
    iter_backend_app_python_files,
)


_REQUESTS_METHODS = {"get", "post", "put", "delete", "patch", "request"}
_HTTPX_METHODS = {"get", "post", "put", "delete", "patch", "request", "stream"}


def _has_kw(call: ast.Call, name: str) -> bool:
    return any(kw.arg == name for kw in call.keywords if kw.arg is not None)


def _func_name(expr: ast.expr) -> str | None:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        base = _func_name(expr.value)
        return f"{base}.{expr.attr}" if base else expr.attr
    return None


def test_http_calls_have_explicit_timeouts() -> None:
    """
    Repo policy: outbound HTTP calls must set explicit timeouts.

    Covered cases (best-effort):
    - requests.<method>(..., timeout=...)
    - httpx.<method>(..., timeout=...)
    - urllib.request.urlopen(..., timeout=...) / urlopen(..., timeout=...)
    - httpx.Client/AsyncClient(..., timeout=...)

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_HTTP_TIMEOUTS=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_HTTP_TIMEOUTS")

    violations: list[tuple[Path, int, str]] = []
    for path in iter_backend_app_python_files(include_tests=True):
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            name = _func_name(node.func)
            if not name:
                continue

            # requests.get/post/...
            if name.startswith("requests.") and name.split(".", 1)[1] in _REQUESTS_METHODS:
                if not _has_kw(node, "timeout"):
                    violations.append((path, node.lineno, f"{name}(...) missing timeout="))
                continue

            # httpx.get/post/... (direct module calls)
            if name.startswith("httpx.") and name.split(".", 1)[1] in _HTTPX_METHODS:
                if not _has_kw(node, "timeout"):
                    violations.append((path, node.lineno, f"{name}(...) missing timeout="))
                continue

            # httpx.Client/AsyncClient construction should set default timeout
            if name in {"httpx.Client", "httpx.AsyncClient"}:
                if not _has_kw(node, "timeout"):
                    violations.append((path, node.lineno, f"{name}(...) missing timeout="))
                continue

            # urlopen(..., timeout=...) (direct or imported)
            if name in {"urlopen", "urllib.request.urlopen"}:
                if not _has_kw(node, "timeout"):
                    violations.append((path, node.lineno, f"{name}(...) missing timeout="))
                continue

    if not violations:
        return

    details = "\n".join(
        f"- {p.relative_to(backend_dir())}:{line_number} {label}"
        for p, line_number, label in sorted(violations, key=lambda x: (str(x[0]), x[1]))
    )
    message = (
        f"{len(violations)} outbound HTTP call(s) missing explicit timeout under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_HTTP_TIMEOUTS=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)

