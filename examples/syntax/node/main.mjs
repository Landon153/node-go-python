import { mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
class User {
  constructor(name) { this.name = name; }
  greet() { return `Hi, ${this.name}`; }
}
function divide(a, b) {
  if (b === 0) throw new Error('division by zero');
  return a / b;
}
const xs = [1, 2, 3, 4];
const copy = [...xs]; copy[0] = 99;
const scores = new Map([['Ada', 9]]);
let error;
try { divide(1, 0); } catch (e) { error = e.message; }
const dir = await mkdtemp(join(tmpdir(), 'node-go-python-'));
let file;
try {
  await writeFile(join(dir, 'hello.txt'), 'hello', 'utf8');
  file = await readFile(join(dir, 'hello.txt'), 'utf8');
} finally { await rm(dir, { recursive: true, force: true }); }
console.log(JSON.stringify({
  greeting: new User('Ada').greet(), even: xs.filter(x => x % 2 === 0),
  squared: xs.map(x => x * x), total: xs.reduce((a, b) => a + b, 0),
  sorted: [10, 2, 1].sort((a, b) => a - b), first_two: xs.slice(0, 2),
  original_first: xs[0], copied_first: copy[0], score: scores.get('Ada'),
  has_missing: scores.has('Bob'), unique: [...new Set([1, 1, 2])],
  parsed: JSON.parse('{"active":true}').active,
  parsed_integer: Number.parseInt('42', 10), error,
  regex: /^[a-z]+$/.test('hello'), hex: Buffer.from('hi').toString('hex'),
  codepoints: [...'Việt'].length, bytes: Buffer.byteLength('Việt', 'utf8'),
  big_integer: (2n ** 60n + 1n).toString(),
  date: new Date('2024-01-02T03:04:05Z').toISOString().replace('.000Z', 'Z'),
  file_roundtrip: file,
}));
