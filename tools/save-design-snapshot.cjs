'use strict';
// Capture a small, reproducible static sample without checking out the old branch.
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const {load} = require('cheerio');
const root = path.resolve(__dirname, '..');
const ref = process.argv[2] || 'origin/main';
const label = process.argv[3] || 'main';
if (!/^[a-z0-9-]+$/.test(label)) throw Error('Use a simple snapshot directory name');
const git = (...args) => execFileSync('git', args, {cwd: root});
const commit = git('rev-parse', '--verify', `${ref}^{commit}`).toString().trim();
const date = git('show', '-s', '--format=%cI', commit).toString().trim();
const tree = new Set(git('ls-tree', '-r', '--name-only', commit).toString().trim().split('\n'));
const pages = [
  ['首页', 'index.html'], ['归档', 'archives/index.html'], ['关于', 'about/index.html'],
  ['技术文章 · Java 内存', '2020/12/17/java-memory/index.html'],
  ['生活文章 · 年度回顾', '2024/01/22/my-2023/index.html'],
  ['中文简历', 'resume/index.html'], ['英文简历', 'resume-en/index.html']
].filter(([,file]) => tree.has(file));
const selected = new Set(pages.map(([,file]) => file));
const prefix = `/design-history/${label}/`;
const output = path.join(root, 'source', prefix);
if (fs.existsSync(output)) throw Error(`Snapshot already exists: ${output}`);
const assets = new Set();
const missing = new Set();
const hosts = new Set(['wxxlamp.cn', 'www.wxxlamp.cn', 'wxxlamp.github.io', 'www.wxxlamp.github.io']);
function local(raw, from) {
  if (!raw || /^(#|data:|mailto:|tel:|javascript:)/i.test(raw)) return null;
  let url;
  try { url = new URL(raw, `https://wxxlamp.cn/${from}`); } catch { return null; }
  if (!hosts.has(url.hostname)) return null;
  let file = decodeURIComponent(url.pathname).replace(/^\//, '');
  if (!file || file.endsWith('/')) file += 'index.html';
  return {file, suffix: url.search + url.hash};
}
function assetUrl(raw, from) {
  const target = local(raw, from);
  if (!target) return raw;
  if (!tree.has(target.file)) { missing.add(target.file); return raw; }
  if (!target.file.endsWith('.html')) assets.add(target.file);
  return prefix + target.file + target.suffix;
}
function rewriteCss(css, from) {
  return css.replace(/url\(\s*(['"]?)(.*?)\1\s*\)/g, (_,q,url)=>`url(${q}${assetUrl(url,from)}${q})`)
    .replace(/(@import\s+)(['"])([^'"]+)\2/g, (_,start,q,url)=>start+q+assetUrl(url,from)+q);
}
function write(file, content) {
  const dest = path.join(output, file);
  fs.mkdirSync(path.dirname(dest), {recursive:true});
  fs.writeFileSync(dest, content);
}
for (const [,file] of pages) {
  const $ = load(git('show', `${commit}:${file}`).toString());
  // Keep historical presentation, but do not submit visits or comments from the archive.
  $('script').each((_,el)=>{
    if (/busuanzi|baidu-tongji|visitors\.js|av-min\.js|Valine|new Valine|hm\.baidu/i.test($(el).attr('src') || $(el).text())) $(el).remove();
  });
  $('link[rel=canonical],link[rel=alternate],meta[name=robots],script[type="application/ld+json"]').remove();
  $('head').append('<meta name="robots" content="noindex, nofollow">');
  $('head').append(`<meta name="design-snapshot" content="${label}@${commit}">`);
  $('[src],link[href],video[poster]').each((_,el)=>{
    for (const attr of ['src','href','poster']) if ($(el).attr(attr)) $(el).attr(attr,assetUrl($(el).attr(attr),file));
  });
  $('[style]').each((_,el)=>$(el).attr('style',rewriteCss($(el).attr('style'),file)));
  $('style').each((_,el)=>$(el).text(rewriteCss($(el).text(),file)));
  $('a[href]').each((_,el)=>{
    const target = local($(el).attr('href'),file);
    if (!target) return;
    if (selected.has(target.file)) $(el).attr('href',prefix+target.file.replace(/index\.html$/,'')+target.suffix);
    else if (tree.has(target.file) && !target.file.endsWith('.html')) $(el).attr('href',assetUrl($(el).attr('href'),file));
    else $(el).removeAttr('href').attr('aria-disabled','true').attr('title','此链接未收录到页面快照');
  });
  write(file,$.html());
}
const copied = new Set();
while ([...assets].some(file=>!copied.has(file))) {
  for (const file of [...assets]) {
    if (copied.has(file)) continue;
    copied.add(file);
    let content = git('show', `${commit}:${file}`);
    if (file.endsWith('.css')) content = rewriteCss(content.toString(),file);
    write(file,content);
  }
}
const manifest = {ref,commit,date,pages:pages.map(([title,file])=>({title,file,current:'/'+file.replace(/index\.html$/,'')})),assets:[...copied].sort(),missingAssets:[...missing].sort(),notes:['External image/CDN URLs remain external.','Analytics and comment submission scripts removed.','Uncaptured internal navigation disabled.']};
write('manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({prefix,commit,pages:pages.length,assets:copied.size,missing:[...missing]},null,2));
