# Load tests (k6)

> 🧠 **Smoke: does it work? Load: does it meet the target? Stress: where does it break? Spike: does it scale? Soak: does it leak?**

## Profiles

Every script supports the same five profiles. They're defined once in [lib/common.js](lib/common.js).

| Profile | Shape | Question |
|---------|-------|----------|
| `smoke` (default) | 1 user, 30 s | Does the script and the API work at all? |
| `load` | target rate, 5 min | Do we meet the NFR numbers? |
| `stress` | 1× → 2× → 3× target | Where does it break first? |
| `spike` | 0.1× → **5×** in 10 s | Does autoscaling (HPA / KEDA) react? |
| `soak` | 0.7× target, 1 h | Memory leaks, connection-pool exhaustion, growing lag? |

## Scripts

| # | Script | Target (`load`) | Thresholds = NFRs |
|---|--------|-----------------|-------------------|
| 1 | [01-product-catalog.js](01-product-catalog.js) | 100 pages/s | page p95 < 300 ms |
| 2 | [02-url-shortener.js](02-url-shortener.js) | 2,000 redirects/s | redirect p95 < 20 ms · `HOT=0.9` for the hot-key test |
| 3 | [03-notification-hub.js](03-notification-hub.js) | 500 events/s | intake p95 < 100 ms (end-to-end latency comes from metrics) |
| 4 | [04-order-saga.js](04-order-saga.js) | 200 orders/s | saga p95 < 3 s · no stuck orders |
| 5 | [05-banking-ledger.js](05-banking-ledger.js) | 1,000 commands/s | command → result p95 < 500 ms · no lost commands |

A failed threshold makes k6 exit non-zero, so these can gate CI later.

## Run

```bash
brew install k6

# 1. Deploy the project to kind and expose it (Ingress or port-forward)
kubectl -n shortener port-forward svc/ingress-nginx-controller 8080:80

# 2. Smoke first, always
k6 run testing/load/02-url-shortener.js

# 3. Then the real profile
k6 run -e PROFILE=load  -e BASE_URL=http://localhost:8080 testing/load/02-url-shortener.js
k6 run -e PROFILE=spike -e BASE_URL=http://localhost:8080 testing/load/02-url-shortener.js
```

Override the target rate with `-e RATE=…`. Each script lists its other options at the top.

## While it runs, watch

- `kubectl get hpa -w` or `kubectl get scaledobject`: does it scale?
- consumer lag (Strimzi Kafka Exporter / Grafana): does it drain?
- the k6 machine's own CPU: **if k6 is at 100%, lower the rate or the numbers are fake.**

## Notes

- The scripts assume the API shapes in the project docs (e.g. `POST /links` returns `{code}`). Adjust the field names to match your implementation.
- Seed test data first (products, SKUs with stock). `setup()` creates only what each script needs.
