// Project 3 · Notification Hub: event intake.
// Proves: NFR-7 (500 events/s). Scale workers during the run for NFR-9 / AT-1.
// End-to-end latency (NFR-8, event → provider) comes from service metrics, not from k6:
// watch consumer lag and the "sent" timer in Grafana while this runs.
//
//   k6 run -e PROFILE=load -e BASE_URL=http://localhost:8080 testing/load/03-notification-hub.js
import http from 'k6/http';
import { check } from 'k6';
import { BASE_URL, JSON_HEADERS, scenario, uuid, randomInt } from './lib/common.js';

const USERS = Number(__ENV.USERS || 10000);
const TYPES = ['UserSignedUp', 'PasswordResetRequested', 'OrderShipped', 'OrderDelivered'];

export const options = {
  scenarios: { events: scenario('publish', Number(__ENV.RATE || 500)) },
  thresholds: {
    'http_req_duration{name:publish-event}': ['p(95)<100'],
    http_req_failed: ['rate<0.01'],
  },
};

export function publish() {
  const userId = `user-${randomInt(1, USERS)}`;
  const body = {
    eventId: uuid(),
    eventType: TYPES[randomInt(0, TYPES.length - 1)],
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    correlationId: uuid(),
    payload: { userId, orderId: `order-${randomInt(1, 1e6)}` },
  };
  const res = http.post(`${BASE_URL}/events`, JSON.stringify(body),
    { headers: JSON_HEADERS, tags: { name: 'publish-event' } });
  check(res, { 'status 202': (r) => r.status === 202 });
}
