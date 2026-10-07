// Static server for the page: 127.0.0.1 only, Cache-Control: no-store so edits show on reload.
//   node murmuration-serve.js [port=8766] [root=this folder]
// ./bootstrap.sh runs it in the background for its own checkout. / redirects to murmuration.html
// (query kept); GET /__serve answers with the pid and root, which bootstrap.sh uses to tell its own
// server from anything else on the port. Paths that resolve outside the root, also through a
// symlink, get 403; dotfiles (.git, .serve, .claude, .venv) and directories get 404.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const port = +(process.argv[2] || 8766);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  console.error('usage: node murmuration-serve.js [port=8766] [root]');
  process.exit(2);
}
const root = fs.realpathSync(process.argv[3] || __dirname);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8', '.md': 'text/plain; charset=utf-8',
  '.py': 'text/plain; charset=utf-8', '.pdf': 'application/pdf', '.mp4': 'video/mp4', '.webm': 'video/webm',
};
const inside = p => p.startsWith(root + path.sep);

function send(res, status, body = '', headers = {}) {
  res.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store', ...headers });
  res.end(res.req.method === 'HEAD' ? undefined : body);
}

http.createServer((req, res) => {
  res.on('finish', () => console.log(`${new Date().toISOString()} ${res.statusCode} ${req.method} ${req.url}`));
  if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(req.headers.host || '')) return send(res, 403, 'bad host\n');
  if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, 'GET or HEAD only\n', { Allow: 'GET, HEAD' });
  const q = req.url.indexOf('?');
  const raw = q < 0 ? req.url : req.url.slice(0, q), search = q < 0 ? '' : req.url.slice(q);
  let rel;
  try { rel = decodeURIComponent(raw); } catch { return send(res, 400, 'bad path\n'); }
  if (rel.includes('\0') || rel[0] !== '/') return send(res, 400, 'bad path\n');
  if (rel === '/') return send(res, 302, '', { Location: '/murmuration.html' + search });
  if (rel === '/__serve') return send(res, 200, `murmuration-serve\npid ${process.pid}\nroot ${root}\n`);

  const file = path.resolve(root, '.' + rel);    // resolve first, then require root + separator
  if (!inside(file)) return send(res, 403, 'outside root\n');
  if (path.relative(root, file).split(path.sep).some(s => s[0] === '.')) return send(res, 404, 'not found\n');
  fs.realpath(file, (err, real) => {
    if (err) return send(res, err.code === 'EACCES' ? 403 : 404, 'not found\n');
    if (!inside(real)) return send(res, 403, 'outside root\n');
    fs.stat(real, (err, st) => {
      if (err || !st.isFile()) return send(res, 404, 'not found\n');
      res.writeHead(200, {
        'Content-Type': TYPES[path.extname(real).toLowerCase()] || 'application/octet-stream',
        'Content-Length': st.size, 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
      });
      if (req.method === 'HEAD') return res.end();
      fs.createReadStream(real).on('error', () => res.destroy()).pipe(res);
    });
  });
}).on('error', e => {
  console.error(e.code === 'EADDRINUSE' ? `port ${port} is already in use` : e.message);
  process.exit(1);
}).listen(port, '127.0.0.1', () => console.log(`serving ${root} at http://127.0.0.1:${port}/murmuration.html`));
