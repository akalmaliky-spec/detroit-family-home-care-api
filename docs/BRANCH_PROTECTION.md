# Branch Protection Setup

This file documents the required branch protection rules for the  branch.
These must be configured manually in GitHub Settings (cannot be done via code).

## Steps

1. Go to: **Settings** → **Branches** → **Branch protection rules** → **Add rule**
2. Set **Branch name pattern**: 
3. Enable the following options:

| Setting | Value |
|---------|-------|
| Require a pull request before merging | Enabled |
| Require approvals (min 1) | Enabled |
| Require status checks to pass before merging | Enabled |
| Status check: select  | Selected |
| Require branches to be up to date before merging | Enabled |
| Require conversation resolution before merging | Enabled |
| Require linear history | Optional (recommended) |
| Do not allow force pushes | Enabled |
| Do not allow deletions | Enabled |

## Why

- **No direct pushes to main**: All changes go through reviewed PRs.
- **CI must pass**:  + ============================= test session starts ==============================
platform linux -- Python 3.12.1, pytest-9.0.1, pluggy-1.6.0
rootdir: /workspaces/detroit-family-home-care-api
configfile: pyproject.toml
testpaths: dfhc/tests
plugins: anyio-4.11.0
collected 0 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting dfhc/tests/test_users.py ___________________
ImportError while importing test module '/workspaces/detroit-family-home-care-api/dfhc/tests/test_users.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/python/3.12.1/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
dfhc/tests/test_users.py:2: in <module>
    from fastapi.testclient import TestClient
E   ModuleNotFoundError: No module named 'fastapi'
=========================== short test summary info ============================
ERROR dfhc/tests/test_users.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.14s =============================== must be green before merge.
- **No force push / no delete**: Preserves immutable audit trail.
- **Conversation resolution**: Ensures review comments are addressed.

## Notes

- GitHub Free accounts support branch protection on public repos.
- For private repos on Free plan, branch protection requires GitHub Team or higher.
- The  workflow name in the status check dropdown will appear as .
