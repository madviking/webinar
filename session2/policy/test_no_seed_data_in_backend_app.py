from backend.tests.policy._utils import app_dir, backend_dir, env_flag, enforce_or_warn


def test_backend_app_does_not_contain_seed_data_directories() -> None:
    """
    Repo policy: seed data should not live in backend/app.

    Hard-fail behavior: set QUEAST_POLICY_ENFORCE_NO_SEED_DATA=1.
    """

    enforce = env_flag("QUEAST_POLICY_ENFORCE_NO_SEED_DATA")

    seeds_dirs = sorted(p for p in app_dir().rglob("seeds") if p.is_dir())
    if not seeds_dirs:
        return

    details = "\n".join(f"- {p.relative_to(backend_dir())}/" for p in seeds_dirs)
    message = (
        f"Found {len(seeds_dirs)} seed directory(ies) under backend/app.\n"
        f"Set QUEAST_POLICY_ENFORCE_NO_SEED_DATA=1 to hard-fail.\n\n"
        f"{details}"
    )
    enforce_or_warn(enforce=enforce, message=message)

