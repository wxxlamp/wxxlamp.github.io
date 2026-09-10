'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function widget(file, origin = 'https://wxxlamp.cn', response = {}) {
  const nodes = {};
  const appended = [];
  const timers = new Set();
  let observed;
  const requests = [];
  let created = 0;
  const node = key => nodes[key] ||= {
    hidden: true, textContent: '', dataset: {}, attributes: {},
    querySelector: node,
    addEventListener(name, handler) { this[name] = handler; },
    setAttribute(name, value) { this.attributes[name] = value; },
    appendChild(el) { if (el.src) appended.push(el); if (el.onload) el.onload(); },
    remove() {}
  };
  node('[data-counter-origin]').dataset.counterOrigin = 'https://wxxlamp.cn';
  node('[data-counter-origin]').dataset.countersUrl = 'https://stats.example/api/public/blog-stats';
  node('[data-counter-origin]').dataset.busuanzi = 'true';
  node('[data-comments-repo]').dataset = {
    commentsRepo: 'wxxlamp/wxxlamp.github.io', commentsCategory: 'Announcements', commentsLang: 'zh-CN',
    commentsRepoId: response.repositoryId,
    commentsCategoryId: (response.categories || []).find(item => item.name === 'Announcements')?.id
  };
  const context = vm.createContext({
    URL, AbortController, console: { warn() {} },
    window: { location: { origin, pathname: "/2025/08/15/how-to-use-mac/" } },
    document: { querySelector: node, getElementById: node, createElement: () => node('created-' + created++),
      head: node('head'), body: node('body'), documentElement: { lang: 'zh-CN' } },
    fetch: (url) => { requests.push(url); return response.fetch ? response.fetch(url) : Promise.resolve({ok:true, json:async () => response.stats || {source:'umami-self-hosted',site:{pv:125,uv:50},page:{pv:20,uv:8}}}); },
    MutationObserver: class { constructor(fn) { observed = fn; } observe() {} disconnect() {} },
    setTimeout(fn) { timers.add(fn); return fn; }, clearTimeout(fn) { timers.delete(fn); }
  });
  const source = fs.readFileSync(path.join(__dirname, '../themes/wxx-theme/source/js/src/', file), 'utf8');
  const run = () => vm.runInContext(source, context);
  run();
  return { node, appended, requests, run, update: () => observed(), timeout: () => [...timers].forEach(fn => fn()) };
}

test('Preview and alternate origins never send a counting request', () => {
  for (const origin of ['http://localhost:4000', 'http://127.0.0.1:4000', 'https://wxxlamp.github.io', 'https://preview.example']) {
    const w = widget('counter.js', origin);
    assert.equal(w.appended.length, 0);
    assert.match(w.node('.site-stats__status').textContent, /不计数/);
  }
});

test('Three-way collection keeps Busuanzi hidden and renders only self-hosted counts', async () => {
  const w = widget('counter.js');
  w.run();
  await flush();
  assert.equal(w.appended.length, 1);
  assert.match(w.appended[0].src, /cdn.busuanzi.cc/);
  assert.equal(w.requests.length, 1);
  assert.equal(new URL(w.requests[0]).searchParams.get('path'), '/2025/08/15/how-to-use-mac/');
  assert.equal(w.node('umami_site_pv').textContent, '125');
  assert.equal(w.node('umami_page_uv').textContent, '8');
  assert.equal(w.node('.site-stats__counts').hidden, false);
});

test('Valid zero counts display and invalid page counts leave site counts intact', async () => {
  const w = widget('counter.js', undefined, {stats:{source:'umami-self-hosted',site:{pv:0,uv:0},page:{pv:1,uv:2}}});
  await flush();
  assert.equal(w.node('umami_site_pv').textContent, '0');
  assert.equal(w.node('.site-stats__counts').hidden, false);
  assert.equal(w.node('.page-stats__counts').hidden, true);
});

test('API failures never substitute Busuanzi numbers', async () => {
  for (const fetch of [async () => {throw Error('network');}, async () => ({ok:false}),
    async () => ({ok:true,json:async()=>({source:'busuanzi',site:{pv:99,uv:9}})}),
    async () => ({ok:true,json:async()=>({source:'umami-self-hosted',site:{pv:'1',uv:1}})})]) {
    const w = widget('counter.js', undefined, {fetch});
    w.node('busuanzi_site_pv').textContent = '999';
    await flush();
    assert.equal(w.node('.site-stats__counts').hidden, true);
    assert.match(w.node('.site-stats__status').textContent, /暂不可用/);
    assert.equal(w.node('umami_site_pv').textContent, '');
  }
});

test('Late responses after timeout do not overwrite unavailable state', async () => {
  let resolve;
  const w = widget('counter.js', undefined, {fetch:()=>new Promise(r=>{resolve=r;})});
  await flush();
  w.timeout();
  resolve({ok:true,json:async()=>({source:'umami-self-hosted',site:{pv:1,uv:1}})});
  await flush();
  assert.equal(w.node('.site-stats__counts').hidden, true);
  assert.match(w.node('.site-stats__status').textContent, /暂不可用/);
});

const flush = () => new Promise(resolve => setImmediate(resolve));
test('Missing configured IDs stop the broken widget before a user can submit', async () => {
  const w = widget('comments.js', undefined, { repositoryId: 'real-repository', categories: [] });
  await flush();
  assert.equal(w.appended.length, 0);
  assert.equal(w.node('.comments-retry').hidden, false);
  assert.match(w.node('.comments-status').textContent, /暂时不可用/);
});

test('Comments use the verified repository/category pair and page language', async () => {
  const w = widget('comments.js', undefined, {
    repositoryId: 'real-repository', categories: [{ name: 'Announcements', id: 'real-category' }]
  });
  await flush();
  w.run();
  assert.equal(w.appended.length, 1);
  assert.equal(w.appended[0].attributes['data-repo-id'], 'real-repository');
  assert.equal(w.appended[0].attributes['data-category-id'], 'real-category');
  assert.equal(w.appended[0].attributes['data-lang'], 'zh-CN');
  assert.equal(w.appended[0].attributes['data-mapping'], 'pathname');
  assert.equal(w.node('.comments-status').hidden, true);
});
