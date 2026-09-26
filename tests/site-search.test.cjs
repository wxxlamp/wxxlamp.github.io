'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { searchDocument } = require('../lib/site-search');
const engine = require('../themes/wxx-theme/source/js/src/search-engine');
const html = (lang = 'zh-CN', robots = '') => `<html lang="${lang}"><head><title>测试 - Blog</title><meta name="robots" content="${robots}"></head><body><nav>不要索引导航</nav><h1>线程池</h1><div class="post-meta"><a>技术</a></div><div class="post-tags"><a>Java</a></div><div class="post-content"><p>并发处理</p><pre><code>executor.submit(task)</code></pre><script>secret()</script></div></body></html>`;
test('index excludes private, duplicate, historical and wrong-language pages', () => {
  for (const route of ['resume/index.html', 'resume-en/index.html', 'en/resume/index.html', 'design-history/main/about/index.html', 'index.html', 'archives/index.html', 'en/about/index.html', 'en/resources/index.html', 'tags/Java/page/2/index.html']) assert.equal(searchDocument(route, html()), null, route);
  assert.equal(searchDocument('en/2026/09/26/test/index.html', html()), null);
  assert.equal(searchDocument('about/index.html', html('zh-CN', 'noindex')), null);
});
test('public content retains code and taxonomy, excludes scripts and navigation', () => {
  const doc = searchDocument('2026/09/26/test/index.html', html());
  assert.match(doc.body, /executor.submit\(task\)/);
  assert.doesNotMatch(doc.body, /secret|不要索引/);
  assert.deepEqual(doc.categories, ['技术']); assert.deepEqual(doc.tags, ['Java']);
  for (const route of ['about/index.html', 'resources/index.html', 'resources/course/test/index.html', 'tags/Java/index.html']) assert.ok(searchDocument(route, html()));
  assert.ok(searchDocument('en/2026/09/26/test/index.html', html('en')));
});
const entries = [
  { title: 'Java 线程池', kind: 'post', categories: ['技术'], tags: ['并发'], body: 'executor.submit(task) 优化', description: '' },
  { title: 'Other', kind: 'post', categories: ['生活'], tags: [], body: 'Java', description: '' }
];
test('partial Chinese, code, case-insensitive multiword, typo and ranked search', () => {
  const records = engine.prepare(entries);
  for (const query of ['线程', 'JAVA 优化', 'executor.submit', 'Jvaa', '技术', '并发']) assert.equal(engine.search(records, query)[0].entry.title, entries[0].title, query);
  assert.equal(engine.search(records, 'java')[0].entry.title, entries[0].title);
  assert.equal(engine.search(records, 'Java 不存在').length, 0);
  assert.equal(engine.search(records, '').length, 0);
  assert.equal(engine.search(records, '', { category: '生活' }).length, 1);
  assert.equal(engine.search(records, 'Java', { tag: '并发' }).length, 1);
  assert.equal(engine.search(records, 'Java', { kind: 'resource' }).length, 0);
});
