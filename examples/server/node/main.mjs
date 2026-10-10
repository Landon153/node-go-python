import http from 'node:http';
const port = Number(process.env.PORT ?? 3000);
function integer(value, min, max) {
  if (value === null || value.length > 8 || !/^-?(0|[1-9][0-9]*)$/.test(value)) throw new Error('invalid_query');
  const n = Number(value);
  if (!Number.isSafeInteger(n) || n < min || n > max) throw new Error('invalid_query');
  return n;
}
function reply(res, status, data) {
  res.writeHead(status, { 'content-type': 'application/json' });
  res.end(JSON.stringify(data));
}
const server = http.createServer((req, res) => {
  if (req.method !== 'GET') { res.setHeader('Allow', 'GET'); return reply(res, 405, { error: 'method_not_allowed' }); }
  try {
    const url = new URL(req.url, 'http://localhost');
    const path = decodeURIComponent(url.pathname);
    if (path === '/sum' || path === '/wait') {
      // Reject ambiguous separators and malformed percent escapes consistently.
      if (/[;]|%(?![0-9a-fA-F]{2})/.test(url.search.slice(1))) throw new Error('invalid_query');
    }
    if (path === '/health') return reply(res, 200, { ok: true });
    if (path === '/sum') {
      const a = integer(url.searchParams.get('a'), -1000000, 1000000);
      const b = integer(url.searchParams.get('b'), -1000000, 1000000);
      return reply(res, 200, { sum: a + b });
    }
    if (path === '/wait') {
      const ms = integer(url.searchParams.get('ms') ?? '50', 0, 1000);
      const timer = setTimeout(() => reply(res, 200, { waited_ms: ms }), ms);
      res.once('close', () => clearTimeout(timer));
      return;
    }
    reply(res, 404, { error: 'not_found' });
  } catch { reply(res, 400, { error: 'invalid_query' }); }
});
server.requestTimeout = 5000;
server.headersTimeout = 5000;
server.listen(port, '127.0.0.1', () => console.log(`Node listening on ${port}`));
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => {
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 5000).unref();
});
