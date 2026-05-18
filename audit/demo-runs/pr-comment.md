### FlakeShield PR Comment Example

#### Flaky tests
- **task-timeout** (runs=2, rate=0.50)
- **task-race** (runs=2, rate=0.50)

#### High risk failures
- **semantic-1**
- **semantic-2**

> This branch includes flaky service and race-condition test behavior. FlakeShield flagged repeated timeout failures in the service layer and grouped the semantic timeouts for easier triage.
