# E2E · Project 4 · Order Saga

**Front door:** `order-service` via Ingress (`http://localhost:8080/orders`) · **Spec:** [docs/04-order-saga.md](../../docs/04-order-saga.md)

> **Test data:** seed SKUs with known stock before each run (`PUT /products/{sku}`). Payment declines any order total > 10,000.

| ID | Scope | Given | When | Then | Proves |
|----|-------|-------|------|------|--------|
| E2E-1 | **Core** | `SKU-1` stock 10 | Order 2 × `SKU-1` | `202` straight away; within **5 s** `COMPLETED`, with a timeline of `OrderCreated → PaymentAuthorized → StockReserved` | FR-1–FR-4, NFR-1 |
| E2E-2 | **Core** | — | Order with a total > 10,000 | Within **5 s** `CANCELLED`; stock unchanged | FR-3, NFR-2 |
| E2E-3 | **Core** | `SKU-2` stock 1 | Order 3 × `SKU-2` | Within **5 s** `CANCELLED`; timeline shows `StockUnavailable → PaymentRefunded`; stock still 1 | FR-6, NFR-2 |
| E2E-4 | **Core** | — | Send the same `Idempotency-Key` twice | Same `orderId` both times; only 1 order exists | FR-1 |
| E2E-5 | **Core** | `SKU-3` stock 5 | 20 parallel orders of 1 × `SKU-3` | Exactly 5 `COMPLETED`, 15 `CANCELLED`; stock = 0, never negative | FR-4, NFR-2 |
| E2E-6 | **Core** | 🔧 Debezium connector paused | Place an order, then resume after 30 s | The order still reaches `COMPLETED` | FR-10, NFR-3, AT-3 |
| E2E-7 | Stretch | Order in `STOCK_RESERVED` | `POST /orders/{id}/cancel` | `CANCELLED`; stock released; refunded | FR-8, AT-9 |
| E2E-8 | Stretch | 🔧 Carrier failure rate = 100% | Place an order | `CANCELLED`; stock released; refunded | FR-5, FR-7 |
| E2E-9 | Stretch | — | Place an order | Within **10 s** the customer notification was "sent" (Project 3 stub) | FR-13 |
