// Project 1 · Product Catalog: product page through the gateway.
// Proves: NFR-6 (load balanced), NFR-7 (page p95 < 300 ms).
// Also run it during AT-2 / AT-3 (slow review-service) to watch the circuit breaker.
//
//   k6 run -e PROFILE=load -e BASE_URL=http://localhost:8080 testing/load/01-product-catalog.js
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, scenario, randomInt } from './lib/common.js';

const PRODUCTS = Number(__ENV.PRODUCTS || 100); // product IDs 1..PRODUCTS must exist (seed them first)

export const options = {
  scenarios: { page: scenario('page', Number(__ENV.RATE || 100)) },
  thresholds: {
    'http_req_duration{name:product-page}': ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export function page() {
  const id = randomInt(1, PRODUCTS);
  const res = http.get(`${BASE_URL}/api/catalog/products/${id}/page`, { tags: { name: 'product-page' } });
  check(res, {
    'status 200': (r) => r.status === 200,
    'has product': (r) => r.json('product') !== null,
    // With review-service down, this flips to false. That's the fallback working, not an error.
    'reviews available': (r) => r.json('reviewsAvailable') === true,
  });
}
