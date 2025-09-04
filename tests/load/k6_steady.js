import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '10m', target: 50 },
    { duration: '2m', target: 0 },
  ],
};

const BASE = __ENV.BASE_URL || 'http://localhost:8080';

export default function () {
  const res = http.get(`${BASE}/health`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}

