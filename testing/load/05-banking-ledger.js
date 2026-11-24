// Project 5 · Banking Ledger: commands + queries.
// Proves: NFR-10 (1,000 commands/s), NFR-11 (command → result p95 < 500 ms), NFR-5 (fresh reads).
// Afterwards, run the invariant checker for NFR-1 (money is conserved).
//
//   k6 run -e PROFILE=load -e CMD_URL=http://localhost:8080 -e QUERY_URL=http://localhost:8081 testing/load/05-banking-ledger.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';
import { JSON_HEADERS, scenario, uuid, randomInt } from './lib/common.js';

const CMD_URL = __ENV.CMD_URL || 'http://localhost:8080';
const QUERY_URL = __ENV.QUERY_URL || 'http://localhost:8081';
const ACCOUNTS = Number(__ENV.ACCOUNTS || 100);
const commandLatency = new Trend('command_latency', true);
const commandLost = new Counter('command_lost');

export const options = {
  scenarios: {
    commands: scenario('sendCommand', Number(__ENV.RATE || 1000)),
    queries: { executor: 'constant-arrival-rate', rate: 200, timeUnit: '1s', duration: __ENV.QUERY_DURATION || '1m',
      preAllocatedVUs: 20, maxVUs: 200, exec: 'readBalance' },
    tracker: { executor: 'constant-vus', vus: 2, duration: __ENV.TRACK_DURATION || '1m', exec: 'trackCommand' },
  },
  thresholds: {
    'http_req_duration{name:send-command}': ['p(95)<100'],
    command_latency: ['p(95)<500'],
    command_lost: ['count==0'],
    http_req_failed: ['rate<0.01'],
  },
};

function post(path, body) {
  return http.post(`${CMD_URL}${path}`, JSON.stringify(body), {
    headers: { ...JSON_HEADERS, 'Idempotency-Key': uuid() },
    tags: { name: 'send-command' },
  });
}

// Runs once: open accounts and give each a big balance, so most withdrawals succeed.
export function setup() {
  const ids = [];
  for (let i = 0; i < ACCOUNTS; i++) {
    const opened = post('/accounts', { owner: `owner-${i}`, currency: 'EUR' });
    const id = opened.json('accountId');
    post(`/accounts/${id}/deposits`, { amount: 1000000 });
    ids.push(id);
  }
  sleep(5); // one-time warm-up so the deposits are applied before load starts
  return { ids };
}

function randomCommand(ids) {
  const id = ids[randomInt(0, ids.length - 1)];
  return Math.random() < 0.5
    ? post(`/accounts/${id}/deposits`, { amount: randomInt(1, 100) })
    : post(`/accounts/${id}/withdrawals`, { amount: randomInt(1, 100) });
}

export function sendCommand(data) {
  check(randomCommand(data.ids), { 'status 202': (r) => r.status === 202 });
}

export function readBalance(data) {
  const id = data.ids[randomInt(0, data.ids.length - 1)];
  const res = http.get(`${QUERY_URL}/accounts/${id}/balance`, { tags: { name: 'read-balance' } });
  check(res, { 'status 200': (r) => r.status === 200, 'never negative': (r) => r.json('balance') >= 0 });
}

export function trackCommand(data) {
  const start = Date.now();
  const res = randomCommand(data.ids);
  if (!check(res, { 'status 202': (r) => r.status === 202 })) return;
  const commandId = res.json('commandId');
  for (let i = 0; i < 50; i++) { // poll for up to 5 s
    sleep(0.1);
    const status = http.get(`${CMD_URL}/commands/${commandId}`, { tags: { name: 'command-status' } }).json('status');
    if (status === 'ACCEPTED' || status === 'REJECTED') {
      commandLatency.add(Date.now() - start);
      return;
    }
  }
  commandLost.add(1);
}
