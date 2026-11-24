// Project 4 · Order Saga: order intake + saga duration.
// Proves: NFR-6 (200 orders/s), NFR-7 (order → final state p95 < 3 s), NFR-8 (KEDA, use PROFILE=spike), NFR-1 (no stuck orders).
// Afterwards, run the invariant checker (tools/) for NFR-2.
//
//   k6 run -e PROFILE=load -e BASE_URL=http://localhost:8080 testing/load/04-order-saga.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';
import { BASE_URL, JSON_HEADERS, scenario, uuid, randomInt } from './lib/common.js';

const SKUS = Number(__ENV.SKUS || 20); // SKU-1..SKU-n must be seeded with stock
const sagaDuration = new Trend('saga_duration', true);
const sagaStuck = new Counter('saga_stuck');

export const options = {
  scenarios: {
    orders: scenario('placeOrder', Number(__ENV.RATE || 200)),
    // A few virtual users follow single orders to the end, to measure saga duration.
    tracker: { executor: 'constant-vus', vus: 2, duration: __ENV.TRACK_DURATION || '1m', exec: 'trackOrder' },
  },
  thresholds: {
    'http_req_duration{name:place-order}': ['p(95)<200'],
    saga_duration: ['p(95)<3000'],
    saga_stuck: ['count==0'],
    http_req_failed: ['rate<0.01'],
  },
};

function order() {
  const body = {
    customerId: `customer-${randomInt(1, 1000)}`,
    items: [{ sku: `SKU-${randomInt(1, SKUS)}`, qty: randomInt(1, 3) }],
    shippingAddress: 'Test street 1',
  };
  return http.post(`${BASE_URL}/orders`, JSON.stringify(body), {
    headers: { ...JSON_HEADERS, 'Idempotency-Key': uuid() },
    tags: { name: 'place-order' },
  });
}

export function placeOrder() {
  check(order(), { 'status 202': (r) => r.status === 202 });
}

export function trackOrder() {
  const start = Date.now();
  const res = order();
  if (!check(res, { 'status 202': (r) => r.status === 202 })) return;
  const id = res.json('orderId');
  for (let i = 0; i < 50; i++) { // poll for up to 10 s, never just sleep and hope
    sleep(0.2);
    const status = http.get(`${BASE_URL}/orders/${id}`, { tags: { name: 'order-status' } }).json('status');
    if (status === 'COMPLETED' || status === 'CANCELLED') {
      sagaDuration.add(Date.now() - start);
      return;
    }
  }
  sagaStuck.add(1);
}
