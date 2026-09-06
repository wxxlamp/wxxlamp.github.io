'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { feeds, articleHtml } = require('../lib/blog-feeds');
const settings = { url: 'https://wxxlamp.cn', title: 'A & B', author: 'Wxx', description: 'Full articles', limit: 20 };
const post = { title: 'A < B', description: 'Java & code', date: new Date('2024-01-01T00:00:00Z'), updated: new Date('2024-02-01T00:00:00Z'), permalink: 'https://wxxlamp.cn/2024/example/', content: '<p>正文</p><pre>line 1\nline 2</pre><img src="/images/test.png">' };
test('Atom declares HTML and both formats retain complete multiline content', () => {
  const [atom, rss] = feeds([post], settings);
  assert.match(atom.data, /<content type="html"/);
  assert.ok(atom.data.includes('line 1\nline 2'));
  assert.ok(rss.data.includes('line 1\nline 2'));
  assert.match(atom.data, /A &lt; B/);
  assert.match(atom.data, /https:\/\/wxxlamp.cn\/images\/test.png/);
  assert.match(rss.data, /<content:encoded>/);
});
test('RSS-reader markup has absolute links and no executable script', () => {
  const html = articleHtml('<a href="../other/#part">Read</a><script>alert(1)</script><img src="./photo.png">', post.permalink);
  assert.match(html, /https:\/\/wxxlamp.cn\/2024\/other\/#part/);
  assert.match(html, /https:\/\/wxxlamp.cn\/2024\/example\/photo.png/);
  assert.ok(!html.includes('<script'));
});
test('English feeds have independent paths and self links; original GUIDs stay stable', () => {
  const [atom, rss] = feeds([{ ...post, permalink: 'https://wxxlamp.cn/en/2024/example/' }], { ...settings, prefix: 'en/', language: 'en' });
  assert.equal(atom.path, 'en/atom.xml');
  assert.equal(rss.path, 'en/rss.xml');
  assert.match(atom.data, /xml:lang="en"/);
  assert.match(atom.data, /https:\/\/wxxlamp.cn\/en\/atom.xml/);
  assert.match(rss.data, /<guid isPermaLink="true">https:\/\/wxxlamp.cn\/en\/2024\/example\/<\/guid>/);
});
test('Feed freshness tracks the latest update, independent of publication sorting', () => {
  const older = { ...post, date: new Date('2020-01-01'), updated: new Date('2026-01-01') };
  assert.match(feeds([post, older], settings)[0].data, /<updated>2026-01-01T00:00:00.000Z<\/updated>/);
});
test('Empty feeds remain valid documents', () => {
  const [atom, rss] = feeds([], settings);
  assert.match(atom.data, /<feed /); assert.match(rss.data, /<channel>/);
  assert.ok(!atom.data.includes('<entry>'));
});
