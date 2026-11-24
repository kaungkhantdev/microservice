# End-to-end tests

> 🧠 **One user story, all real services, through the front door.**

## What an E2E test is here

- The whole project is **deployed on kind** (or docker-compose for Project 1, Phase A).
- The test acts like a **user**: it calls the public API and checks what a user would see.
- Async results (Kafka) are checked by **polling with a deadline**, never with a fixed sleep.

## Scenario format

Each project file lists scenarios like this:

| Field | Meaning |
|-------|---------|
| **Given** | the starting state (test data, a stopped service, a config flag) |
| **When** | the action, through the public API |
| **Then** | what must be true, and the deadline for async results |
| **Proves** | the requirement or acceptance test it covers |
| **Scope** | Core or Stretch, same as the requirement |

Some scenarios need **fault injection** (stopping a service, setting a stub's failure rate). They're marked 🔧, and the test controls the fault with `kubectl` or a config flag before it runs.

## Recommended tooling (Java)

A separate Maven module, `testing/e2e`, with one test class per project:

```
testing/e2e/
├── pom.xml                                   # JUnit 5, RestAssured, Awaitility, Jackson
└── src/test/java/practice/e2e/
    ├── ProductCatalogE2ETest.java
    ├── UrlShortenerE2ETest.java
    └── …
```

```java
// Async assertion: poll until true, or fail after 5 s
await().atMost(Duration.ofSeconds(5)).pollInterval(Duration.ofMillis(200)).untilAsserted(() ->
    given().get("/links/{code}/stats", code).then().body("clicks", equalTo(3)));
```

Run it against a deployed cluster:

```bash
mvn -pl testing/e2e verify -De2e.baseUrl=http://localhost:8080
```

**Alternative:** Postman collections run with the Postman CLI (`postman collection run`). This works well for the sync scenarios. Polling async results is easier in Java.

## Scenario files

- [01-product-catalog.md](01-product-catalog.md)
- [02-url-shortener.md](02-url-shortener.md)
- [03-notification-hub.md](03-notification-hub.md)
- [04-order-saga.md](04-order-saga.md)
- [05-banking-ledger.md](05-banking-ledger.md)
