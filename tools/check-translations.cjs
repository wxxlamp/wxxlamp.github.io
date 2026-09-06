'use strict';
const fs = require('node:fs');
const path = require('node:path');
const matter = require('hexo-front-matter');
const base = path.resolve(__dirname, '../source/_posts');
const referenceCatalog = require('../source/_data/references.json');
function referenceIdentity(raw) {
  const pair = referenceCatalog.pairs.find(p => p.zh === raw || p.en === raw);
  if (pair) return pair.zh;
  try {
    const u = new URL(raw);
    if (['wxxlamp.cn', ...referenceCatalog.site_aliases].includes(u.hostname)) {
      let route = decodeURI(u.pathname).replace(/^\/en\//, '/');
      route = referenceCatalog.route_aliases[route] || route;
      return 'site:' + route + u.search + u.hash;
    }
  } catch {}
  return raw;
}
const originals = fs.readdirSync(base).filter(n => n.endsWith('.md'));
const issues = [];
const missing = [];
const counts = {};
function structure(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n');
  const blocks = [];
  let fence = null, block = [], prose = [];
  for (const line of lines) {
    const match = line.match(/^\s*(`{3,}|~{3,})(.*)$/);
    if (!fence && match) { fence = match[1]; block = [line]; }
    else if (fence) {
      block.push(line);
      if (match && match[1][0] === fence[0] && match[1].length >= fence.length && !match[2].trim()) { blocks.push(block.join('\n')); fence = null; }
    } else prose.push(line);
  }
  if (fence) blocks.push(block.join('\n'));
  return { blocks, prose: prose.join('\n'), headings: prose.filter(x => /^#{1,6}\s/.test(x)).map(x => x.match(/^#+/)[0]) };
}
for (const name of originals) {
  const target = path.join(base, 'en', name);
  if (!fs.existsSync(target)) { missing.push(name); continue; }
  let source, english;
  try { source = matter.parse(fs.readFileSync(path.join(base, name), 'utf8')); english = matter.parse(fs.readFileSync(target, 'utf8')); }
  catch (error) { issues.push({ file: name, issue: 'front matter', detail: error.message }); continue; }
  if (english.lang !== 'en' || english.translation_of !== name.slice(0, -3)) issues.push({ file: name, issue: 'translation metadata' });
  for (const key of ['date', 'tags', 'categories']) if (JSON.stringify(source[key]) !== JSON.stringify(english[key])) issues.push({ file: name, issue: 'changed ' + key });
  const a = structure(source._content), b = structure(english._content);
  if (JSON.stringify(a.blocks) !== JSON.stringify(b.blocks)) issues.push({ file: name, issue: 'code block mismatch', source: a.blocks.length, english: b.blocks.length });
  if (a.headings.join(',') !== b.headings.join(',')) issues.push({ file: name, issue: 'heading structure mismatch', source: a.headings.length, english: b.headings.length });
  const urls = text => [...new Set(text.match(/https?:\/\/[^\s<>"')\]]+/g) || [])];
  const targetUrls = new Set(urls(english._content).map(referenceIdentity));
  const dropped = urls(source._content).filter(url => !targetUrls.has(referenceIdentity(url)));
  if (dropped.length) issues.push({ file: name, issue: 'missing URLs', urls: dropped });
  const clean = text => text.replace(/`[^`]*`/g, '').replace(/https?:\/\/\S+/g, '');
  const originalProse = clean(a.prose), translatedProse = clean(b.prose);
  const cjk = (translatedProse.match(/[\u4e00-\u9fff]/g) || []).length;
  counts[name] = { source: originalProse.length, english: translatedProse.length, cjk };
  if (translatedProse.length < originalProse.length * .8) issues.push({ file: name, issue: 'translation unusually short', ...counts[name] });
  if (cjk > 80) issues.push({ file: name, issue: 'Chinese prose remains', cjk });
}
// English is a curated selection. Chinese-only posts are intentional.
const report = { total: originals.length, translated: originals.length - missing.length, chineseOnly: missing.length, issues, counts };
console.log(JSON.stringify(report, null, 2));
if (issues.length) process.exitCode = 1;
