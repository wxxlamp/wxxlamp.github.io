'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {load}=require('cheerio');
const root=path.resolve(__dirname,'../public');
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const files=walk(root).filter(p=>p.endsWith('.html') && !path.relative(root,p).startsWith('design-history'+path.sep));
const pages=new Map();const titles=new Set();
for(const file of files){
 const relative=path.relative(root,file).split(path.sep).join('/');
 const html=fs.readFileSync(file,'utf8');const $=load(html);
 const canonical=$('link[rel=canonical]').attr('href');
 assert.equal($('title').length,1,relative);assert.ok($('title').text().trim(),relative);
 assert.equal($('meta[name=description]').length,1,relative);
 assert.ok($('meta[name=description]').attr('content').length>0,relative);
 assert.equal($('link[rel=canonical]').length,1,relative);
 assert.equal(canonical,new URL(relative.replace(/index\.html$/,''),'https://wxxlamp.cn/').href,relative);
 assert.equal($('meta[property="og:url"]').attr('content'),canonical,relative);
 const en=$('html').attr('lang')==='en';const brand=en?"Sibo's Blog":'王星星的魔灯';
 assert.equal($('meta[property="og:site_name"]').attr('content'),brand,relative);
 assert.equal($('.brand-name').text(),brand,relative);
 assert.equal($('meta[name=author]').attr('content'),en?'Sibo Wang':'王星星',relative);
 assert.ok(!titles.has($('title').text()),'Duplicate title: '+relative);titles.add($('title').text());
 const noindex=$('meta[name=robots]').attr('content').includes('noindex');
 const schema=$('script[type="application/ld+json"]');
 assert.equal(schema.length,noindex?0:1,relative);
 if(!noindex){
  const data=JSON.parse(schema.text());assert.equal(data['@context'],'https://schema.org');
  const entity=data['@graph'][1];assert.equal(entity.url,canonical);
  if(/^(en\/)?\d{4}\//.test(relative)){
   assert.equal(entity['@type'],'BlogPosting');assert.ok(entity.datePublished);assert.equal(entity.author.name,en?'Sibo Wang':'王星星');
   assert.equal(entity.inLanguage,en?'en':'zh-CN');
  }
 }
 if(en)assert.doesNotMatch(html,/Xingxing|XINGXING|Xingxing’s Notes/);
 pages.set(canonical,{$,relative,noindex});
}
for(const [url,page] of pages){
 const alts=page.$('link[hreflang]');
 if(alts.length){
  assert.equal(alts.length,3,page.relative);
  alts.each((_,el)=>{
   const lang=page.$(el).attr('hreflang'),target=page.$(el).attr('href');
   assert.ok(pages.has(target),'Missing hreflang: '+target);
   const back=pages.get(target).$(`link[hreflang="${page.$('html').attr('lang')}"]`).attr('href');
   assert.equal(back,url,'Missing reciprocal hreflang: '+page.relative+' '+lang);
  });
 }
}
const sitemap=load(fs.readFileSync(path.join(root,'sitemap.xml'),'utf8'),{xmlMode:true});
const urls=sitemap('loc').map((_,e)=>sitemap(e).text()).get();
assert.equal(urls.length,new Set(urls).size);
assert.deepEqual(new Set(urls),new Set([...pages].filter(([,p])=>!p.noindex).map(([u])=>u)));
assert.equal(sitemap('lastmod').length,0);
assert.match(fs.readFileSync(path.join(root,'robots.txt'),'utf8'),/Sitemap: https:\/\/wxxlamp.cn\/sitemap.xml/);
for(const relative of ['about/index.html','en/about/index.html']){
 const $=load(fs.readFileSync(path.join(root,relative),'utf8'));
 assert.equal($('.post-content h1,.post-content h2,.post-content h3').length,0);
 assert.ok($('.about-qr').length);
 assert.ok($('a[href="https://www.xiaohongshu.com/user/profile/63dbcba3000000002702896e"]').length);
}
const atom=load(fs.readFileSync(path.join(root,'en/atom.xml'),'utf8'),{xmlMode:true});
assert.equal(atom('feed > title').text(),"Sibo's Blog");assert.equal(atom('feed > author > name').text(),'Sibo Wang');
console.log(`Validated SEO on ${pages.size} pages, ${urls.length} sitemap URLs, reciprocal language variants, server-rendered English identity, structured data and private-page exclusions.`);
