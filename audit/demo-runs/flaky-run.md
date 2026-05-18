# Flaky Demo Run

- Run type: intentionally flaky scenario
- `npm run test:flaky`
- Total tests: 10
- Passed: 6
- Failed: 4

Failures introduced in flaky mode:
- `validates the timeout signature` → network timeout
- `exercises race behavior` → race condition
- `checks service timeout reporting` → semantic timeout
- `checks retry timeout policy` → semantic retry timeout

This run is designed to show real flaky behavior and recurring failure patterns that FlakeShield can triage.
