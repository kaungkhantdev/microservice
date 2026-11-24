# E2E · Project 1 · Product Catalog

**Front door:** `api-gateway` (`http://localhost:8080/api/...`) · **Spec:** [docs/01-product-catalog.md](../../docs/01-product-catalog.md)

| ID | Scope | Given | When | Then | Proves |
|----|-------|-------|------|------|--------|
| E2E-1 | **Core** | Product 42 with 2 reviews by users 7 and 9 | `GET /api/catalog/products/42/page` | `200` with the product, 2 reviews and both reviewer names | FR-4, FR-5 |
| E2E-2 | **Core** | — | `POST /api/catalog/products`, then `GET` it | `201`, then the same product comes back | FR-1, FR-5 |
| E2E-3 | **Core** | Product 42 exists | `POST /api/reviews` for product 42, then open the page | The new review is on the page | FR-2, FR-4 |
| E2E-4 | **Core** | 🔧 `review-service` scaled to 0 | Open the page | `200` **within 1.5 s**, `reviews: []`, `reviewsAvailable: false` | FR-7, NFR-1, AT-3 |
| E2E-5 | **Core** | 🔧 `review-service` restarted with a new address | Open the page | Reviews are back, with no config change | FR-6, AT-1 |
| E2E-6 | Stretch | Services run on an internal network only | Call `catalog-service` directly on its port | Connection refused / not reachable | NFR-15 |
| E2E-7 | Stretch | No JWT | `POST /api/catalog/products` | `401` from the gateway | FR-9, AT-7 |
| E2E-8 | Stretch | Rate limit = 10 req/s | 50 requests in 1 s from one client | Some responses are `429` | FR-10, AT-6 |
