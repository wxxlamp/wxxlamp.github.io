const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const path = require('node:path');

const script = path.resolve(__dirname, '../scripts/site-analytics.js');
let enabled;
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {
  require: createRequire(script),
  hexo: { extend: { helper: { register(name, helper) { enabled = helper; } } } }
});

test('Clarity is available on public home and article pages', () => {
  for (const page of [{ path: 'index.html' }, { path: 'en/index.html' }, { path: '2026/09/06/article/index.html' }]) {
    assert.equal(enabled.call({ page }), true);
  }
});

test('Clarity is excluded from protected, private, and opted-out pages', () => {
  for (const page of [
    { path: 'resume/index.html' }, { path: 'resume-en/index.html' },
    { path: 'en/resume/index.html' }, { path: 'design-history/main/index.html' },
    { path: 'example/index.html', password: 'protected' },
    { path: 'example/index.html', noindex: true },
    { path: 'example/index.html', sitemap: false },
    { path: 'alias/index.html', canonical_path: 'resume/index.html' }
  ]) {
    assert.equal(enabled.call({ page }), false, JSON.stringify(page));
  }
});
