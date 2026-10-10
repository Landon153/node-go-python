import { setTimeout as sleep } from 'node:timers/promises';
// Two consumers bound how many jobs may be in flight; no unbounded Promise.all.
const values = new Array(6);
let next = 0, active = 0, maxActive = 0;
async function worker() {
  while (next < values.length) {
    const index = next++;
    active++; maxActive = Math.max(maxActive, active);
    try { await sleep(30); values[index] = index * 2; }
    finally { active--; }
  }
}
await Promise.all([worker(), worker()]);
console.log(JSON.stringify({ values, max_active: maxActive }));
