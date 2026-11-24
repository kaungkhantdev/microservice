// Project 2 · URL Shortener: redirect hot path.
// Proves: NFR-1 (redirect p95 < 20 ms), NFR-3 (cache hits), NFR-4 (2,000 redirects/s), NFR-6 (HPA, use PROFILE=spike).
// Hot-key test (AT-7): -e HOT=0.9 sends 90% of traffic to one link.
//
//   k6 run -e PROFILE=load -e BASE_URL=http://localhost:8080 testing/load/02-url-shortener.js
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, JSON_HEADERS, scenario, randomInt } from './lib/common.js';

const LINKS = Number(__ENV.LINKS || 100);
const HOT = Number(__ENV.HOT || 0); // share of traffic that goes to link #0

export const options = {
  scenarios: { redirect: scenario('redirect', Number(__ENV.RATE || 2000)) },
  thresholds: {
    'http_req_duration{name:redirect}': ['p(95)<20'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

// Runs once: create the links that the test will hit.
export function setup() {
  const codes = [];
  for (let i = 0; i < LINKS; i++) {
    const res = http.post(`${BASE_URL}/links`, JSON.stringify({ url: `https://example.com/page/${i}` }),
      { headers: JSON_HEADERS, tags: { name: 'create-link' } });
    check(res, { 'link created': (r) => r.status === 201 });
    codes.push(res.json('code'));
  }
  return { codes };
}

export function redirect(data) {
  const code = Math.random() < HOT ? data.codes[0] : data.codes[randomInt(0, data.codes.length - 1)];
  // redirects: 0 → don't follow the 302, measure only our service
  const res = http.get(`${BASE_URL}/${code}`, { redirects: 0, tags: { name: 'redirect' } });
  check(res, { 'status 302': (r) => r.status === 302 });
}

// After the run, compare total clicks in stats with the number of redirects k6 sent (NFR-10).
