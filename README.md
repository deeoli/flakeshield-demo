# FlakeShield Demo

A small, realistic Node + Vitest demo repository built to show FlakeShield value immediately.

## What this repo demonstrates

- Healthy test coverage for core logic
- Intentional flaky async/timing tests
- Recurring failures with repeated failure patterns
- Semantic grouping of timeout and network issues
- GitHub Actions integration with FlakeShield
- PR comment generation and artifact upload


![FlakeShield Pipeline](Flakeshield-Introduction.png)

## Repo structure

- `src/` – tiny task helpers and async service simulation
- `tests/` – stable tests and flaky scenario coverage
- `.github/workflows/flakeshield.yml` – workflow that runs tests twice and calls FlakeShield
- `audit/demo-runs/` – sample demo outputs for healthy and flaky runs

## How to run locally

```bash
cd flakeshield-demo
npm install
npm run test:healthy
npm run test:flaky
```

The `test:healthy` run uses a clean service path. The `test:flaky` run introduces timing and network race conditions.

## Flaky scenarios implemented

- `fetchTaskStatus()` simulates random network timeout behavior
- `retryFetchTaskStatus()` exercises retry behavior under intermittent failure
- `fetchWithRace()` models race-condition failures between fast and stale requests
- Semantic failure cluster with repeated `Network timeout while calling task service` errors

## Expected outputs

- `test-results/junit-healthy.xml` from the healthy CI run
- `test-results/junit-flaky.xml` from the flaky CI run
- `outputs/flake_report.md` with grouped failures, semantic clustering, and risk prioritization
- `outputs/pr_comment.md` with compact GitHub-ready CI summaries
- Downloadable GitHub Actions artifacts containing reports and test results
- FlakeShield detection of repeated timeout and race-condition failures

## Trigger flaky behavior

The workflow does two runs:
1. Healthy run: `npm run test:healthy`
2. Flaky run: `npm run test:flaky`

In GitHub Actions, FlakeShield compares these runs and surfaces repeated failures.

## Real Output Examples

- [FlakeShield Markdown Report](./examples/flake_report.md)
- [PR Comment Example](./examples/pr_comment.md)

---

> This demo is intentionally small, practical, and ready to use for public showcases.
