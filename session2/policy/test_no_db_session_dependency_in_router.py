import ast
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    enforce_or_warn,
    iter_backend_app_python_files,
)


def _expr_name(expr: ast.expr) -> str | None:
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        base = _expr_name(expr.value)
        return f"{base}.{expr.attr}" if base else expr.attr
    return None


def _is_depends_call(expr: ast.expr) -> bool:
    if not isinstance(expr, ast.Call):
        return False
    fn = _expr_name(expr.func)
    return fn in {"Depends", "fastapi.Depends"}


def _is_session_annotation(expr: ast.expr | None) -> bool:
    if expr is None:
        return False
    name = _expr_name(expr)
    return name in {"Session", "sqlmodel.Session"}


def _iter_args_with_defaults(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[tuple[ast.arg, ast.expr | None]]:
    pairs: list[tuple[ast.arg, ast.expr | None]] = []

    pos_args = node.args.args
    pos_defaults = node.args.defaults
    pos_default_start = len(pos_args) - len(pos_defaults)
    for idx, arg in enumerate(pos_args):
        default = pos_defaults[idx - pos_default_start] if idx >= pos_default_start else None
        pairs.append((arg, default))

    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        pairs.append((arg, default))

    return pairs


def test_router_files_do_not_inject_db_session_dependency() -> None:
    """
    Repo policy: routers should not inject DB sessions (they should depend on services instead).

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_NO_DB_SESSION_IN_ROUTER=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_NO_DB_SESSION_IN_ROUTER")

    router_files = [p for p in iter_backend_app_python_files(include_tests=False) if p.name == "router.py"]
    if not router_files:
        return

    violations: list[tuple[Path, int, str]] = []
    for path in router_files:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for arg, default in _iter_args_with_defaults(node):
                if not _is_session_annotation(arg.annotation):
                    continue
                if arg.arg in {"db", "session"} and default is not None and _is_depends_call(default):
                    violations.append((path, arg.lineno, f"{node.name}({arg.arg}: Session = Depends(...))"))

    if not violations:
        return

    details = "\n".join(
        f"- {p.relative_to(backend_dir())}:{line_number} {snippet}"
        for p, line_number, snippet in sorted(violations, key=lambda x: (str(x[0]), x[1]))
    )
    message = (
        f"{len(violations)} router function(s) appear to inject a DB session dependency.\n"
        f"Set QUEAST_POLICY_ENFORCE_NO_DB_SESSION_IN_ROUTER=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)
