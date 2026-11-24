# Practice Projects: Microservices, Kafka + Kubernetes (Java / Spring Boot)

Four projects, from beginner to advanced. Start with **synchronous** microservices, then climb the **event-driven ladder**:

| Step | Project | Motto | Architecture style |
|------|---------|-------|--------------------|
| 0️⃣ **Call** other services | [Product Catalog](00-product-catalog.md) | *Find it, route it, protect it.* | Request-driven: registry + gateway + circuit breaker |
| 1️⃣ **React** to events | [Notification Hub](01-notification-hub.md) | *Publish once, notify many.* | Event notification + fan-out |
| 2️⃣ **Coordinate** with events | [Order Saga](02-order-saga.md) | *Every step has an undo.* | Choreographed saga + outbox |
| 3️⃣ **Remember** everything as events | [Banking Ledger](03-banking-ledger.md) | *The log is the truth. Everything else is a view.* | Event sourcing + CQRS |

> 🧠 **Sync first, then async: Call → React → Coordinate → Remember.**

## What each project teaches

| # | Level | Main skills | Kubernetes | Core effort |
|---|-------|-------------|------------|-------------|
| 0 | Beginner → Intermediate | Eureka, Spring Cloud Gateway, Resilience4j, Config Server (no Kafka yet) | Services + DNS, Ingress, ConfigMaps | a weekend |
| 1 | Intermediate | Consumer groups, keys, idempotency, DLQ | Deployments, ConfigMaps, probes, Strimzi | a weekend |
| 2 | Upper-intermediate | Saga, outbox + Debezium, Schema Registry, retry topics | Helm, KEDA, PDBs, graceful shutdown | about a week |
| 3 | Advanced | Event sourcing, replay, exactly-once, schema evolution | Argo CD, blue/green, NetworkPolicies, mTLS, ACLs | 1–2 weeks |

## Request-driven vs event-driven in one minute

| | Request-driven (Project 0) | Event-driven (Projects 1–3) |
|---|---|---|
| Services talk by | HTTP call, then wait | Publish an event, don't wait |
| If the other side is down | Caller fails (unless it has a fallback) | Events wait in Kafka |
| Key tools | Registry, gateway, circuit breaker | Kafka, outbox, idempotent consumers |

Real systems use both: **synchronous at the edges, event-driven inside.**

## Event-driven architecture in one minute

- **Event** = a fact that already happened (`OrderShipped`). Named in the past tense.
- **Command** = a request that may be rejected (`WithdrawMoney`).
- **Producers don't know consumers.** Add a new consumer without touching the producer.
- **Synchronous at the edges, async inside.** Clients use REST; services talk only through Kafka.
- **The price:** eventual consistency, duplicates and ordering issues. Every project teaches how to pay it.

## How to read a project doc

Every doc has the same short layout: **motto → what you build → architecture style → architecture image → scope → Spring Boot → requirements → acceptance tests**.

- **FR** = what the system *does*. **NFR** = how *well* it does it. **AT** = a test that proves both.
- **Core** = build this first, end to end. **Stretch** = add later, one at a time.

| Project | Core | Stretch |
|---------|------|---------|
| 0 | 14 requirements + 5 tests | 13 + 5 |
| 1 | 15 requirements + 4 tests | 13 + 3 |
| 2 | 13 requirements + 3 tests | 18 + 6 |
| 3 | 11 requirements + 2 tests | 29 + 7 |

## Shared conventions

**Event envelope** (every message): `eventId` · `eventType` · `eventVersion` · `occurredAt` · `correlationId` · `causationId` · `payload`

**Topic names:** `<domain>.<entity>.<kind>`, e.g. `orders.order.events`, `notifications.email.commands`.

**Kafka defaults:** 3 brokers (KRaft, Strimzi) · `replication.factor=3` · `min.insync.replicas=2` · producers `acks=all` + `enable.idempotence=true`.

**Machine:** kind cluster on a laptop with ≥ 16 GB RAM (≈ 8 GB for the cluster).

## Tech stack

| Concern | Choice |
|---------|--------|
| Language / framework | Java 21 or 25 (LTS) · Spring Boot 3.5.x or 4.x |
| Microservices (Project 0) | Spring Cloud: Gateway, Netflix Eureka, Config, OpenFeign, Circuit Breaker (Resilience4j) |
| Kafka | Spring for Apache Kafka (`KafkaTemplate`, `@KafkaListener`) · Kafka Streams (Project 3) |
| Data | Spring Data JPA + Flyway + PostgreSQL |
| Health / metrics | Actuator probes · Micrometer + Prometheus · OpenTelemetry tracing |
| Tests | JUnit 5 · Testcontainers (`@ServiceConnection`) · Awaitility · `TopologyTestDriver` |
| Build / images | Maven multi-module · `mvn spring-boot:build-image` → `kind load docker-image` |

## Repo layout

```
microservice/
├── pom.xml                      # Maven parent
├── libs/event-envelope/         # shared event classes + serde
├── services/
│   ├── product-catalog/         # Project 0 modules
│   ├── notification-hub/        # Project 1 modules
│   ├── order-saga/              # Project 2 modules
│   └── banking-ledger/          # Project 3 modules
├── deploy/
│   ├── compose/                 # Project 0 Phase A (docker-compose)
│   ├── kind/                    # cluster config
│   ├── strimzi/                 # Kafka, KafkaTopic, KafkaUser, KafkaConnect
│   └── <project>/               # manifests / Helm charts
├── tools/                       # load, chaos, invariant scripts
├── docs/                        # you are here
└── Makefile                     # make up / down / test
```

## Diagrams

Images in [`images/`](images/) are generated by [`images/generate_diagrams.py`](images/generate_diagrams.py), which needs only the Python standard library. Edit the script, then run `python3 docs/images/generate_diagrams.py`.
