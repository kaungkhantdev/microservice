# E2E · Project 5 · Banking Ledger

**Front doors:** `command-api` and `query-api` via Ingress · **Spec:** [docs/05-banking-ledger.md](../../docs/05-banking-ledger.md)

> Commands are async: **send → get `commandId` → poll `GET /commands/{id}`** until `ACCEPTED` or `REJECTED`, then check the read side with `minVersion` or by polling.

| ID | Scope | Given | When | Then | Proves |
|----|-------|-------|------|------|--------|
| E2E-1 | **Core** | — | Open account A, deposit 500, withdraw 100 | All commands `ACCEPTED` within **2 s**; balance = 400, version 3 | FR-1, FR-2, FR-3, FR-6, FR-9 |
| E2E-2 | **Core** | A has 50 | Withdraw 100 | `REJECTED` (insufficient funds); balance still 50 | FR-3 |
| E2E-3 | **Core** | — | Send the same deposit twice with one `Idempotency-Key` | One deposit only | FR-6 |
| E2E-4 | **Core** | A has 100 | 50 parallel withdrawals of 10 | Exactly 10 `ACCEPTED`; balance = 0, never below | NFR-4, AT-4 |
| E2E-5 | **Core** | 100 accounts with activity | Rebuild the balance projection into `balances_v2` | Same checksum as `balances_v1` | FR-14, NFR-8, AT-2 |
| E2E-6 | **Core** | Many random deposits and withdrawals | Run the invariant checker | Sum of balances = deposits − withdrawals; no negatives | NFR-1 |
| E2E-7 | Stretch | A has 300, B has 0 | Transfer 100 from A to B | A = 200, B = 100, transfer `COMPLETED` | FR-4 |
| E2E-8 | Stretch | B is closed | Transfer 100 from A to B | Transfer `REVERSED`; A unchanged | FR-4 |
| E2E-9 | Stretch | Known history | `GET /accounts/A/balance?asOf=<time>` | Matches the balance at that time | FR-12, AT-9 |
| E2E-10 | Stretch | A frozen | Withdraw 10 | `REJECTED`; deposits still accepted | FR-5 |
