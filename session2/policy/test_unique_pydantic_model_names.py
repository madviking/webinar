import ast
from collections import defaultdict
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


def test_pydantic_model_class_names_are_unique() -> None:
    """
    Repo policy: avoid duplicate Pydantic model names across modules.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_UNIQUE_PYDANTIC_MODEL_NAMES=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_UNIQUE_PYDANTIC_MODEL_NAMES")

    occurrences: dict[str, list[Path]] = defaultdict(list)
    for path in iter_backend_app_python_files(include_tests=False):
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name.startswith("_"):
                continue
            bases = [_expr_name(base) for base in node.bases]
            if any(base_name and base_name.endswith("BaseModel") for base_name in bases):
                occurrences[node.name].append(path)

    duplicates = {name: paths for name, paths in occurrences.items() if len(paths) > 1}
    if not duplicates:
        return

    lines = []
    for name in sorted(duplicates):
        paths = sorted({p.relative_to(backend_dir()) for p in duplicates[name]})
        lines.append(f"- {name}: {', '.join(str(p) for p in paths)}")

    message = (
        f"Found {len(duplicates)} duplicate Pydantic model name(s) under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_UNIQUE_PYDANTIC_MODEL_NAMES=1 to hard-fail.\n\n"
        + "\n".join(lines)
    )
    enforce_or_warn(enforce=enforce, message=message)

