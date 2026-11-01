# Contributing

Open an issue to discuss substantial physics or API changes before implementation.
Small fixes and documentation corrections can be submitted directly as pull requests.

Create the environment described in the README, then install `python -m pip install
-e '.[dev]'`. Run `pytest -q`, `ruff check utherm tests examples`, `python -m build`,
and `python -m twine check dist/*` before opening a pull request.

For numerical changes, include the physical argument, units, relevant reference,
and a regression test that can detect the failure. Preserve upstream notices.
Avoid committing city data, simulation output, credentials, or machine-specific
paths. Provide a synthetic reproducer when reporting a defect.

Changes are contributed under GPL-3.0-or-later. State the origin and license of
any third-party code introduced in a contribution.
