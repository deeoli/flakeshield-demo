# FlakeShield Walkthrough

**Thesis:** Reduce CI noise. Increase engineering signal.

This walkthrough follows one failed CI run through the full FlakeShield intelligence loop — no implementation code required.

Related: [Before vs After](../showcase/transformation.md) · [Raw CI](../showcase/raw-ci.txt) · [FlakeShield output](../showcase/flakeshield-output.txt)

---

## Problem

Typical CI output after a failed run:

```text
FAIL  PaymentService.test_payment_creation
  Error: Cannot read property 'validate' of null
      at PaymentService.processPayment (.../payment.js:142:15)
  [RETRY 1/2] ... FAILED AGAIN

FAIL  PaymentService.test_refund_creation
  NullPointerException: Cannot read property 'validate' of null

FAIL  PaymentService.test_payment_checkout
  Error: Cannot read property 'validate' of null

FAIL  DatabaseService.test_read_connection
  Error: Connection refused to database
  NETWORK ERROR — ECONNREFUSED 127.0.0.1:5432

FAIL  DatabaseService.test_write_connection
  Error: Connection refused to database

FAIL  CheckoutFlow.test_checkout_timeout
  TimeoutError: Request timeout after 30000ms
  TIMEOUT — gateway did not respond

SUMMARY: 6 failed | 2 passed | 8 total
```

Engineers see:

- **Duplicated failures** — the same null-pointer error three times with different test names
- **Retries** — `FAILED AGAIN` without clear root cause
- **Repeated stack traces** — line numbers and paths that obscure the signal
- **No prioritization** — every failure looks equally urgent

The question is not *whether* CI failed. It is *what actually broke*, and *where to start*.

---

## Phase 1 — Failure Grouping

**Question:** What failed?

| Input | Output |
|-------|--------|
| 6 failures | 3 root causes |

FlakeShield normalizes error signatures (strips paths, line numbers, timestamps) and groups failures by root cause:

```text
Detected 3 failure groups

Signal compression:
  6 failures -> 3 root causes

Group 1 — NullPointerException in payment validation
  Affected Tests:
    - PaymentService.test_payment_checkout
    - PaymentService.test_payment_creation
    - PaymentService.test_refund_creation

Group 2 — Connection refused to database
  Affected Tests:
    - DatabaseService.test_read_connection
    - DatabaseService.test_write_connection

Group 3 — Request timeout after Xms
  Affected Tests:
    - CheckoutFlow.test_checkout_timeout
```

Three separate red failures in CI become **three investigation targets**.

---

## Phase 2 — Failure Memory

**Question:** Has this failed before?

FlakeShield persists failure signatures across runs in `data/failure-history.json`.

**First run** (no history):

```text
New root causes:       3
Recurring root causes: 0

Seen Before: NO
Occurrences: 1
Status: NEW
```

**Second run** (same failures):

```text
New root causes:       0
Recurring root causes: 3

Seen Before: YES
Occurrences: 2
Status: RECURRING
```

```text
Seen Before: NO  →  Seen Before: YES
Occurrences: 1   →  Occurrences: 2+
```

A parser tells you what failed once. Memory tells you whether it is **becoming a pattern**.

---

## Phase 3 — Risk Prioritization

**Question:** What deserves attention first?

FlakeShield scores each group deterministically from occurrence count, affected tests, and recurrence — then sorts **highest risk first**:

```text
Risk order:
  HIGH    (0.93)  NullPointerException in payment validation
  MEDIUM  (0.51)  Connection refused to database
  LOW     (0.36)  Request timeout after Xms
```

Example — top priority group:

```text
Top Priority Group:
NullPointerException in payment validation

Risk:
HIGH (0.93)
```

Not every root cause deserves the same attention. Risk ranking answers: **start here**.

---

## Phase 4 — Actionable Summary

**Question:** Why does this matter?

Scores alone do not guide investigation. FlakeShield adds deterministic, human-readable explanations:

```text
Why This Matters:
Recurring failure affecting multiple tests. This issue appears repeatedly
and may indicate a systemic problem.

TOP INSIGHTS

1. Highest Risk Issue:
   NullPointerException in payment validation

Reason:
   Recurring across multiple tests.

2. Stability Signal:
   3 recurring failure groups detected.

3. Investigation Focus:
   Start with the highest recurring group.
```

Engineers get **decision support**, not just metrics.

---

## Final Transformation

| | Raw CI | FlakeShield |
|---|--------|-------------|
| Failures | 6 | 3 root causes |
| Priority | None | Highest risk first |
| History | Unknown | Recurring: YES |
| Guidance | Logs only | Why it matters |

```text
Raw CI:
  6 failures

FlakeShield:
  3 root causes

Highest Priority:
  NullPointerException in payment validation

Recurring:
  YES

Risk:
  HIGH

Why:
  Recurring failure affecting multiple tests. This issue appears repeatedly
  and may indicate a systemic problem.
```

---

## Intelligence Flow

```text
Raw CI
    ↓
Root Causes          Phase 1 — What failed?
    ↓
Historical Memory    Phase 2 — Has this failed before?
    ↓
Risk Ranking         Phase 3 — What deserves attention first?
    ↓
Actionable Guidance  Phase 4 — Why does this matter?
```

---

## Run it yourself

```bash
cd flakeshield-demo
python src/report.py
```

- **Input:** `sample-results/junit.xml`
- **Output:** `reports/failure-summary.txt`
- **History:** `data/failure-history.json` (builds across runs)

Run twice to see memory and recurrence shift from NEW to RECURRING.

---

## What this demo is (and is not)

**This repo demonstrates** the FlakeShield intelligence story end to end.

**This repo does not include** the production engine, GitHub Action wrapper, or LLM-based analysis — those live in separate repos and real-world CI validation.

The next meaningful question is not *can we add another layer?* — it is *do engineers find this output useful in practice?*
