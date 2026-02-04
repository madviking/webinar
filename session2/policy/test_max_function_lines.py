import ast
from pathlib import Path

from backend.tests.policy._utils import (
    backend_dir,
    env_flag,
    env_int,
    enforce_or_warn,
    iter_backend_app_python_files,
)


def test_backend_app_functions_do_not_exceed_max_lines() -> None:
    """
    Repo policy: keep functions small enough to review.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_MAX_FUNCTION_LINES=1.
    Threshold override: set QUEAST_POLICY_MAX_FUNCTION_LINES (default: 200).
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_MAX_FUNCTION_LINES")
    max_lines = env_int("QUEAST_POLICY_MAX_FUNCTION_LINES", default=200)

    violations: list[tuple[str, str, int]] = []

    for path in iter_backend_app_python_files(include_tests=True):
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(path))

        class Visitor(ast.NodeVisitor):
            def __init__(self) -> None:
                self.stack: list[str] = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
                self._check(node)
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
                self._check(node)
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

            def _check(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
                if not getattr(node, "end_lineno", None) or not node.lineno:
                    return
                length = node.end_lineno - node.lineno + 1
                if length <= max_lines:
                    return
                qualified = ".".join([*self.stack, node.name]) if self.stack else node.name
                violations.append((str(path), qualified, length))

        Visitor().visit(tree)

    if not violations:
        return

    violations.sort(key=lambda item: item[2], reverse=True)
    lines = "\n".join(
        f"- {Path(file_path).relative_to(backend_dir())}:{qualified}: {length}"
        for file_path, qualified, length in violations
    )
    message = (
        f"{len(violations)} function(s) exceed {max_lines} lines under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_MAX_FUNCTION_LINES=1 to hard-fail.\n"
        f"Set QUEAST_POLICY_MAX_FUNCTION_LINES to tune the threshold.\n\n"
        f"{lines}"
    )
    enforce_or_warn(enforce=enforce, message=message)
