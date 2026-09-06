'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {load} = require('cheerio');
const root = path.resolve(__dirname,'..');
const base = 'design-history/';
const manifest = JSON.parse(fs.readFileSync(path.join(root,'source',base,'main/manifest.json')));
const pages = [base+'index.html',...manifest.pages.map(p=>base+'main/'+p.file)];
for (const file of [...pages,...manifest.assets.map(f=>base+'main/'+f),base+'main/manifest.json']) {
  assert.ok(fs.readFileSync(path.join(root,'public',file)).equals(fs.readFileSync(path.join(root,'source',file))),`Snapshot changed during Hexo build: ${file}`);
}
for (const file of pages) {
  const $ = load(fs.readFileSync(path.join(root,'public',file),'utf8'));
  assert.match($('meta[name=robots]').attr('content'),/noindex/);
  assert.equal($('script[src*="busuanzi"],script[src*="baidu-tongji"],script[src*="Valine"]').length,0);
  $('[src],link[href],a[href]').each((_,el)=>{
    const url=$(el).attr('src') || $(el).attr('href');
    if (!url?.startsWith('/') || url.startsWith('//')) return;
    const target=decodeURIComponent(new URL(url,'https://wxxlamp.cn').pathname).replace(/^\//,'').replace(/\/$/,'/index.html') || 'index.html';
    assert.ok(fs.existsSync(path.join(root,'public',target)),`Missing snapshot dependency: ${file} -> ${url}`);
    if ($(el).is('script,link') && file!==base+'index.html') assert.ok(url.startsWith('/'+base),'Snapshot must use isolated assets: '+url);
  });
}
assert.doesNotMatch(fs.readFileSync(path.join(root,'public/sitemap.xml'),'utf8'),/design-history/);
console.log(`Validated ${manifest.pages.length} archived pages, comparison index, ${manifest.assets.length} local assets, unchanged build output and noindex exclusions.`);
