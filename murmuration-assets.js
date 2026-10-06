// Check or refresh the page's bird tables from their committed model exports.
//   node murmuration-assets.js [--write] [murmuration.html]
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const args = process.argv.slice(2);
const write = args.includes('--write');
const html = path.resolve(args.find(a => !a.startsWith('--')) || path.join(__dirname, 'murmuration.html'));
const read = name => JSON.parse(fs.readFileSync(path.join(__dirname, name), 'utf8'));
const round = value => Array.isArray(value) ? value.map(round) : Number(value.toFixed(3));
const falcon = read('falcon/outline/peregrine-outline.json');
const starling = read('starling/outline/starling-low15.json');
const expected = {
  STARLING: { spread: round(starling.pose.flap_mid), flexed: round(starling.pose.upstroke) },
  FALCON: {
    halfSpanM: falcon.halfSpanM, aOriginM: falcon.aOriginM,
    keys: falcon.keys, knots: round(falcon.knots),
    wing: falcon.keys.map(key => round(falcon.wing[key])),
    body: round(falcon.body), tail: round(falcon.tail), tailFan: round(falcon.tailFan),
  },
};
let source = fs.readFileSync(html, 'utf8');
let mismatches = 0;
for (const [name, table] of Object.entries(expected)) {
  const pattern = new RegExp(`^const ${name} = \\{.*?^\\};`, 'ms');
  const match = source.match(pattern);
  if (!match) throw new Error(`Missing ${name} table in ${html}`);
  const actual = vm.runInNewContext(`${match[0]}\n${name}`, {}, { timeout: 1000 });
  const matches = Object.keys(table).length === Object.keys(actual).length &&
    Object.entries(table).every(([key, value]) => JSON.stringify(value) === JSON.stringify(actual[key]));
  if (!matches) {
    mismatches++;
    if (write) {
      const lines = Object.entries(table).map(([key, value]) => `  ${key}: ${JSON.stringify(value)},`);
      source = source.replace(pattern, `const ${name} = {\n${lines.join('\n')}\n};`);
    }
  }
  console.log(`${name}: ${matches ? 'matches model export' : write ? 'updated from model export' : 'OUT OF DATE'}`);
}
if (write && mismatches) fs.writeFileSync(html, source);
if (!write && mismatches) process.exitCode = 1;
