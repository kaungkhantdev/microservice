# Testing

> 🧠 **Unit proves the code. Integration proves the wiring. E2E proves the story. Load proves the numbers.**

## Test layers

| Layer | Question it answers | Where | Tool | When |
|-------|---------------------|-------|------|------|
| Unit | Does this class work? | each service's `src/test` | JUnit 5, Mockito, `TopologyTestDriver` | every build |
| Integration | Does this service work with real Kafka, DB and Redis? | each service's `src/test` | Testcontainers (`@ServiceConnection`) | every build |
| **End-to-end** | Does the **user story** work across all services? | [`e2e/`](e2e/) | JUnit 5 + RestAssured + Awaitility (or Postman CLI) | after deploying to kind |
| **Load** | Does it meet the **numbers** (p95, throughput, scaling)? | [`load/`](load/) | k6 | before calling a project done |
| Chaos | Does it survive kills, broker loss, node drains? | acceptance tests in each project doc | `kubectl`, Chaos Mesh (stretch) | per project |

## Rules

1. **Test through the front door.** E2E and load tests call only public endpoints (gateway / Ingress), never a service's internals.
2. **Never `sleep()` for async results. Poll until true, or time out.** Kafka flows finish "eventually", so assert with a deadline, e.g. Awaitility `await().atMost(5, SECONDS).until(...)`.
3. **Every test traces back to a requirement.** Each scenario lists the `FR`, `NFR` or `AT` it proves.
4. **Load-test from outside the cluster.** If k6 maxes out your laptop's CPU, you're measuring k6, not your service.

## Per project

| # | Project | E2E scenarios | Load test | Headline number |
|---|---------|---------------|-----------|-----------------|
| 1 | Product Catalog | [e2e/01-product-catalog.md](e2e/01-product-catalog.md) | [load/01-product-catalog.js](load/01-product-catalog.js) | page p95 < 300 ms |
| 2 | URL Shortener | [e2e/02-url-shortener.md](e2e/02-url-shortener.md) | [load/02-url-shortener.js](load/02-url-shortener.js) | redirect p95 < 20 ms at 2,000/s |
| 3 | Notification Hub | [e2e/03-notification-hub.md](e2e/03-notification-hub.md) | [load/03-notification-hub.js](load/03-notification-hub.js) | 500 events/s |
| 4 | Order Saga | [e2e/04-order-saga.md](e2e/04-order-saga.md) | [load/04-order-saga.js](load/04-order-saga.js) | 200 orders/s, saga p95 < 3 s |
| 5 | Banking Ledger | [e2e/05-banking-ledger.md](e2e/05-banking-ledger.md) | [load/05-banking-ledger.js](load/05-banking-ledger.js) | 1,000 commands/s, result p95 < 500 ms |

See [e2e/README.md](e2e/README.md) and [load/README.md](load/README.md) for how to write and run them.
