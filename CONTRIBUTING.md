# Contributing

Open an issue to discuss substantial physics or API changes before implementation.
Small fixes and documentation corrections can be submitted directly as pull requests.

Follow the [development guide](docs/DEVELOPMENT.md) for setup, lint, coverage,
API documentation, and distribution checks. For numerical changes, explain the
physical argument, units, assumptions, and reference; add a regression test that
can detect the failure. Do not update reference values merely to make tests pass.

Bug reports should include `utherm doctor --json`, the exact version or commit,
and a small synthetic reproducer. Never include credentials or private city data.
Preserve upstream copyright notices and state the origin and license of any new
third-party code. Contributions are licensed under GPL-3.0-or-later.
