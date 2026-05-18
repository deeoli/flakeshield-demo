# FlakeShield Report

- Runs considered: **2**

## 📊 Summary
- 2 failure groups
- 0 flaky tests
- 0 high-risk failures

## 🔥 Fix First
- **tests/flaky.spec.js::Flaky integration scenarios > validates the timeout signature**
  - Risk: **LOW** (0.27)
  - Seen in 1/2 runs
  - Why this matters: new failure pattern that may indicate a regression.
  - Preview: Network timeout while calling task service
  - Fingerprint: `network timeout while calling task service`

- **tests/flaky.spec.js::Flaky integration scenarios > exercises race behavior**
  - Risk: **LOW** (0.17)
  - Seen in 1/2 runs
  - Why this matters: new failure pattern that may indicate a regression.
  - Preview: Race condition detected during task fetch
  - Fingerprint: `race condition detected during task fetch`

## 🧠 Known vs Novel
- Known failures: 0
- Novel failures: 2
  - Novel fingerprint: `network timeout while calling task service`
  - Novel fingerprint: `race condition detected during task fetch`

## 🔎 Failure Group Details
### Group 1 — 3 occurrences
- Fingerprint: `network timeout while calling task service`
- Examples:
  - `junit-flaky.xml` — **tests/flaky.spec.js::Flaky integration scenarios > validates the timeout signature** — Network timeout while calling task service
  - `junit-flaky.xml` — **tests/flaky.spec.js::Semantic failure cluster > checks service timeout reporting** — Network timeout while calling task service
  - `junit-flaky.xml` — **tests/flaky.spec.js::Semantic failure cluster > checks retry timeout policy** — Network timeout while calling task service

### Group 2 — 1 occurrences
- Fingerprint: `race condition detected during task fetch`
- Examples:
  - `junit-flaky.xml` — **tests/flaky.spec.js::Flaky integration scenarios > exercises race behavior** — Race condition detected during task fetch

## 🧠 Semantic failure groups (ML-assisted, experimental)
- Similarity threshold: **0.80**

### Semantic Group 1 — 3 occurrences
- Representative: `Network timeout while calling task service`
Members:
- `junit-flaky.xml` — **tests/flaky.spec.js::Flaky integration scenarios > validates the timeout signature** — Network timeout while calling task service
- `junit-flaky.xml` — **tests/flaky.spec.js::Semantic failure cluster > checks service timeout reporting** — Network timeout while calling task service
- `junit-flaky.xml` — **tests/flaky.spec.js::Semantic failure cluster > checks retry timeout policy** — Network timeout while calling task service

### Semantic Group 2 — 1 occurrences
- Representative: `Race condition detected during task fetch`
Members:
- `junit-flaky.xml` — **tests/flaky.spec.js::Flaky integration scenarios > exercises race behavior** — Race condition detected during task fetch

## 📊 Top flakiest tests

| Test ID | Runs | Passes | Fails |
|---|---:|---:|---:|
| `tests/flaky.spec.js::Flaky integration scenarios > exercises race behavior` | 2 | 1 | 1 |
| `tests/flaky.spec.js::Flaky integration scenarios > validates the timeout signature` | 2 | 1 | 1 |
| `tests/flaky.spec.js::Semantic failure cluster > checks retry timeout policy` | 2 | 1 | 1 |
| `tests/flaky.spec.js::Semantic failure cluster > checks service timeout reporting` | 2 | 1 | 1 |

## Runs included
- `test-results/junit-flaky.xml`
- `test-results/junit-healthy.xml`
