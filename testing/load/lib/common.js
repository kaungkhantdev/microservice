// Shared helpers for every load test.
// Pick a profile with:  k6 run -e PROFILE=smoke|load|stress|spike|soak <script>.js

export const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
export const JSON_HEADERS = { 'Content-Type': 'application/json' };

/**
 * Returns a k6 scenario for the chosen PROFILE.
 * @param {string} exec  name of the exported function to run
 * @param {number} rate  target requests per second for the "load" profile
 */
export function scenario(exec, rate) {
  const name = __ENV.PROFILE || 'smoke';
  const low = Math.max(1, Math.ceil(rate / 10));
  const vus = { preAllocatedVUs: 50, maxVUs: 1000 };
  const profiles = {
    // Does it work at all?
    smoke: { executor: 'constant-vus', vus: 1, duration: '30s' },
    // Does it meet the target at normal load?
    load: { executor: 'constant-arrival-rate', rate, timeUnit: '1s', duration: '5m', ...vus },
    // Where does it break?
    stress: {
      executor: 'ramping-arrival-rate', startRate: low, timeUnit: '1s', ...vus,
      stages: [
        { target: rate, duration: '2m' },
        { target: rate * 2, duration: '3m' },
        { target: rate * 3, duration: '3m' },
        { target: 0, duration: '1m' },
      ],
    },
    // Does it survive a sudden burst (and scale)?
    spike: {
      executor: 'ramping-arrival-rate', startRate: low, timeUnit: '1s', ...vus,
      stages: [
        { target: low, duration: '30s' },
        { target: rate * 5, duration: '10s' },
        { target: rate * 5, duration: '1m' },
        { target: low, duration: '1m' },
      ],
    },
    // Does it leak over time?
    soak: { executor: 'constant-arrival-rate', rate: Math.ceil(rate * 0.7), timeUnit: '1s', duration: '1h', ...vus },
  };
  if (!profiles[name]) throw new Error(`Unknown PROFILE "${name}". Use smoke, load, stress, spike or soak.`);
  return { ...profiles[name], exec };
}

export function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
