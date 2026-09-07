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
  const node = key => nodes[key] ||= {
    hidden: true, textContent: '', dataset: {}, attributes: {},
    querySelector: node,
    addEventListener(name, handler) { this[name] = handler; },
    setAttribute(name, value) { this.attributes[name] = value; },
    appendChild(el) { appended.push(el); if (el.onload) el.onload(); },
    remove() {}
  };
  node('[data-counter-origin]').dataset.counterOrigin = 'https://wxxlamp.cn';
  node('[data-comments-repo]').dataset = {
    commentsRepo: 'wxxlamp/wxxlamp.github.io', commentsCategory: 'Announcements', commentsLang: 'zh-CN',
    commentsRepoId: response.repositoryId,
    commentsCategoryId: (response.categories || []).find(item => item.name === 'Announcements')?.id
  };
  const context = vm.createContext({
    URL, AbortController, console: { warn() {} },
    window: { location: { origin } },
    document: { querySelector: node, getElementById: node, createElement: () => node('script-' + appended.length),
      head: node('head'), documentElement: { lang: 'zh-CN' } },
    fetch: () => { throw new Error('The categories API must not be called from the browser'); },
    MutationObserver: class { constructor(fn) { observed = fn; } observe() {} disconnect() {} },
    setTimeout(fn) { timers.add(fn); return fn; }, clearTimeout(fn) { timers.delete(fn); }
  });
  const source = fs.readFileSync(path.join(__dirname, '../themes/wxx-theme/source/js/src/', file), 'utf8');
  const run = () => vm.runInContext(source, context);
  run();
  return { node, appended, run, update: () => observed(), timeout: () => [...timers].forEach(fn => fn()) };
}

test('Preview and alternate origins never send a counting request', () => {
  for (const origin of ['http://localhost:4000', 'http://127.0.0.1:4000', 'https://wxxlamp.github.io', 'https://preview.example']) {
    const w = widget('counter.js', origin);
    assert.equal(w.appended.length, 0);
    assert.match(w.node('.site-stats__status').textContent, /不计数/);
  }
});

test('Production loads the counter once and only displays valid results', () => {
  const w = widget('counter.js');
  w.run();
  assert.equal(w.appended.length, 1);
  assert.equal(w.node('.site-stats__counts').hidden, true);
  w.node('busuanzi_value_site_pv').textContent = '125';
  w.node('busuanzi_value_site_uv').textContent = '50';
  w.update();
  assert.equal(w.node('.site-stats__counts').hidden, false);
  assert.equal(w.node('.site-stats__status').hidden, true);
});

test('Invalid results, network errors, and timeouts never display false counts', () => {
  for (const failure of ['invalid', 'network', 'timeout']) {
    const w = widget('counter.js');
    if (failure === 'invalid') {
      w.node('busuanzi_value_site_pv').textContent = '1';
      w.node('busuanzi_value_site_uv').textContent = '2';
      w.update();
    } else if (failure === 'network') w.appended[0].onerror();
    else w.timeout();
    assert.equal(w.node('.site-stats__counts').hidden, true);
    assert.match(w.node('.site-stats__status').textContent, /暂不可用/);
  }
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
