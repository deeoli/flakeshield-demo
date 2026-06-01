# From CI Noise to Signal

A 10-second view of what FlakeShield does to a typical failed CI run.

```text
Raw CI  -->  FlakeShield  -->  Actionable Output
```

Full artifacts: [raw-ci.txt](./raw-ci.txt) | [flakeshield-output.txt](./flakeshield-output.txt)

---

## Raw CI

What engineers usually scroll through:

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

Problems:

- Duplicated failures and repeated stack traces
- Mixed signals: NullPointerException, NETWORK ERROR, TIMEOUT, RETRY
- No ranking — everything looks equally urgent
- Hard to answer: **how many root causes?**

---

## FlakeShield

Same run, after grouping, memory, risk scoring, and actionable summaries:

```text
Detected 3 failure groups

Signal compression:
  6 failures -> 3 root causes

Top Priority Group:
NullPointerException in payment validation

Risk:
HIGH

Recurring:
YES

Why it matters:
Recurring failure affecting multiple tests. This issue appears repeatedly
and may indicate a systemic problem.

Investigation Focus:
Start with the highest recurring group.
```

---

## Difference

| | Raw CI | FlakeShield |
|---|--------|-------------|
| **Failures shown** | 6 separate failures | 3 root causes |
| **Duplicates** | Same NPE stack trace × 3 | One payment validation group |
| **Priority** | None — read everything | Top priority called out first |
| **History** | Not visible | Recurring: YES |
| **Risk** | Not ranked | HIGH on highest-impact group |
| **Guidance** | Logs only | Why it matters + where to start |

**At a glance:**

```text
Raw CI:        6 failures
FlakeShield:   3 root causes

Highest Priority:  NullPointerException in payment validation
Recurring:         YES
Risk:              HIGH
```

---

## The four questions FlakeShield answers

| Phase | Question |
|-------|----------|
| 1 — Grouping | What failed? |
| 2 — Memory | Has this failed before? |
| 3 — Risk | What should I investigate first? |
| 4 — Summary | Why does this matter? |

---

## Try it locally

```bash
python src/report.py
```

Live output: `reports/failure-summary.txt`
