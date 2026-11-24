# E2E · Project 2 · URL Shortener

**Front door:** Ingress (`http://localhost:8080`) · **Spec:** [docs/02-url-shortener.md](../../docs/02-url-shortener.md)

> Turn off automatic redirect-following in the HTTP client, so you can assert on the `302` itself.

| ID | Scope | Given | When | Then | Proves |
|----|-------|-------|------|------|--------|
| E2E-1 | **Core** | — | `POST /links {url}`, then `GET /{code}` | `302` with `Location` = the original URL | FR-1, FR-2 |
| E2E-2 | **Core** | A new link | Open it 3 times | Within **5 s**, `GET /links/{code}/stats` shows `clicks: 3` | FR-6, FR-7, NFR-10 |
| E2E-3 | **Core** | — | `GET /doesnotexist` | `404` | FR-2 |
| E2E-4 | **Core** | — | `POST /links {url: "not a url"}` | `400` | FR-1 |
| E2E-5 | **Core** | 100 links created | Compare the codes | All codes are unique, 7 chars, Base62 | FR-3 |
| E2E-6 | **Core** | 🔧 Kafka unreachable (brokers scaled to 0) | Open a link | Still `302`, at normal speed | NFR-2, AT-3 |
| E2E-7 | Stretch | Alias `promo` already taken | `POST /links {url, alias: "promo"}` | `409` | FR-4 |
| E2E-8 | Stretch | Link expired | Open it | `410 Gone` | FR-5, AT-8 |
| E2E-9 | Stretch | Link disabled | Open it straight away | `404` (cache evicted) | FR-11, AT-9 |
