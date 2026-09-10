const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { createRequire } = require('node:module');
const path = require('node:path');

const script = path.resolve(__dirname, '../scripts/site-analytics.js');
let enabled;
const helpers = {};
vm.runInNewContext(fs.readFileSync(script, 'utf8'), {
  require: createRequire(script),
  hexo: { extend: { helper: { register(name, helper) {
    helpers[name] = helper;
    if (name === 'clarity_enabled') enabled = helper;
  } } } }
});

const swig = require('swig-templates');
const template = fs.readFileSync(path.resolve(__dirname,
  '../themes/wxx-theme/layout/_script/_analytics/umami.swig'), 'utf8');
function renderUmami(page, overrides = {}) {
  return swig.render(template, { locals: {
    theme: { umami: { enable: true, website_id: 'test-website-id',
      script_url: 'https://cloud.umami.is/script.js', domains: 'wxxlamp.cn', ...overrides } },
    public_analytics_enabled: () => helpers.public_analytics_enabled.call({ page })
  } });
}

test('Umami renders once, restricted to production, grouping query strings and anchors', () => {
  const html = renderUmami({ path: '2026/09/08/article/index.html' });
  assert.equal((html.match(/<script /g) || []).length, 1);
  assert.match(html, /data-domains="wxxlamp.cn"/);
  assert.match(html, /data-exclude-search="true"/);
  assert.match(html, /data-exclude-hash="true"/);
});

test('Umami stays absent when unconfigured, disabled or on private pages', () => {
  for (const overrides of [{ enable: false }, { website_id: '' }]) {
    assert.equal(renderUmami({ path: 'index.html' }, overrides).trim(), '');
  }
  for (const page of [{ path: 'resume/index.html' }, { password: 'secret' }, { noindex: true }]) {
    assert.equal(renderUmami(page).trim(), '');
  }
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


test('Cloud and self-hosted trackers coexist without leaking onto private pages', () => {
  const cloud = {enable:true,website_id:'cloud-id',script_url:'https://cloud.umami.is/script.js'};
  const html = renderUmami({path:'index.html'}, {script_url:'https://self.example/script.js',cloud});
  assert.equal((html.match(/<script /g) || []).length, 2);
  assert.match(html, /self.example/);
  assert.match(html, /cloud-id/);
  assert.equal(renderUmami({password:'private'}, {cloud}).trim(), '');
});
