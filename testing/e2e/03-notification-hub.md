# E2E · Project 3 · Notification Hub

**Front door:** `event-producer` (`http://localhost:8080/events`) · **Spec:** [docs/03-notification-hub.md](../../docs/03-notification-hub.md)

> **Test hook:** each stub provider records what it "sent" and exposes `GET /stub/sent?userId=` (test only), so the test can see deliveries without real email.

| ID | Scope | Given | When | Then | Proves |
|----|-------|-------|------|------|--------|
| E2E-1 | **Core** | — | `POST /events` with `OrderShipped` for user 7 | Within **5 s**, the email stub shows exactly 1 email for user 7 | FR-1, FR-2, FR-5 |
| E2E-2 | **Core** | — | Send the **same event** (same `eventId`) twice | Still exactly 1 email | FR-6, NFR-2 |
| E2E-3 | **Core** | 🔧 Stub failure rate = 100% | Send an event | Within **15 s**, the message is in `notifications.dlq` with error headers | FR-7, FR-8 |
| E2E-4 | **Core** | — | Put malformed JSON straight on `orders.order.events` (`kubectl exec` + console producer) | It lands in the DLQ, and a valid event sent next is still delivered | FR-8, NFR-6 |
| E2E-5 | **Core** | — | Send an unknown event type, then a valid one | The unknown one is skipped, and the valid one is delivered | FR-11 |
| E2E-6 | **Core** | Two events for user 7: A then B | Send both quickly | The stub received A before B | NFR-5 |
| E2E-7 | Stretch | User 7 opted out of SMS | Send `PasswordResetRequested` | Email sent, SMS `SKIPPED_OPT_OUT` | FR-3, AT-7 |
| E2E-8 | Stretch | 🔧 One message in the DLQ, failure rate back to 0% | `POST /admin/dlq/replay` | The message is delivered | FR-9, AT-5 |
| E2E-9 | Stretch | — | `GET /notifications?userId=7` | Shows `SENT` / `FAILED` / `SKIPPED` per notification | FR-10 |
