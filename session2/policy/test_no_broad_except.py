import ast
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    enforce_or_warn,
    iter_backend_app_python_files,
)


def _is_broad_exception_type(expr: ast.expr | None) -> bool:
    if expr is None:
        return True  # bare `except:`
    if isinstance(expr, ast.Name) and expr.id in {"Exception", "BaseException"}:
        return True
    if isinstance(expr, ast.Tuple):
        for elt in expr.elts:
            if isinstance(elt, ast.Name) and elt.id in {"Exception", "BaseException"}:
                return True
    return False


def test_backend_app_has_no_broad_except_blocks() -> None:
    """
    Repo policy: avoid bare `except:` and `except Exception:` blocks.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_NO_BROAD_EXCEPT=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_NO_BROAD_EXCEPT")

    violations: list[tuple[Path, int, str]] = []
    for path in iter_backend_app_python_files(include_tests=True):
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                if not _is_broad_exception_type(handler.type):
                    continue
                line = handler.lineno or node.lineno
                if handler.type is None:
                    label = "except:"
                elif isinstance(handler.type, ast.Name):
                    label = f"except {handler.type.id}:"
                else:
                    label = "except (..):"
                violations.append((path, line, label))

    if not violations:
        return

    details = "\n".join(
        f"- {p.relative_to(backend_dir())}:{line_number} {label}"
        for p, line_number, label in sorted(violations, key=lambda x: (str(x[0]), x[1]))
    )
    message = (
        f"{len(violations)} broad except block(s) found under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_NO_BROAD_EXCEPT=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)

