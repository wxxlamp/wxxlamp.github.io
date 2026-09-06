const test = require('node:test');
const assert = require('node:assert/strict');
const { load } = require('cheerio');
const { pageMetadata, metadataHtml, sitemapXml, renderEnglishUi } = require('../lib/site-seo');
const settings = { origin: 'https://wxxlamp.cn', language: 'en', siteTitle: "Sibo's Blog", author: 'Sibo Wang', taxonomyLabel: value => ({'基础夯实':'Fundamentals'}[value] || value) };
test('English article metadata uses one canonical URL, English identity and safe structured data', () => {
  const meta = pageMetadata({ ...settings, page: {path:'en/2025/01/02/example/index.html',title:'A </script><script>alert(1)</script> & B',description:'A "quoted" explanation.',date:new Date('2025-01-02T00:00:00Z'),content:'<p>Body</p><img src="/cover.png">',categories:[{name:'基础夯实'}]} });
  const $=load(metadataHtml(meta));
  assert.equal($('link[rel=canonical]').attr('href'),'https://wxxlamp.cn/en/2025/01/02/example/');
  assert.equal($('meta[property="og:site_name"]').attr('content'),"Sibo's Blog");
  assert.equal($('meta[name=description]').attr('content'),'A "quoted" explanation.');
  assert.equal($('script').length,1);
  const graph=JSON.parse($('script').text())['@graph'];
  assert.equal(graph[1]['@type'],'BlogPosting');
  assert.equal(graph[1].author.name,'Sibo Wang');
  assert.equal(graph[1].inLanguage,'en');
  assert.equal(graph[1].articleSection[0],'Fundamentals');
  assert.equal(graph[1].image[0],'https://wxxlamp.cn/cover.png');
});
test('Pagination and archive periods have distinct localized titles and descriptions', () => {
  const home=pageMetadata({...settings,page:{path:'en/'}});
  const page2=pageMetadata({...settings,page:{path:'en/page/2/',current:2}});
  const archive=pageMetadata({...settings,page:{path:'en/archives/2025/01/',archive:true,year:2025,month:1}});
  assert.notEqual(home.title,page2.title);
  assert.match(page2.title,/Page 2/);
  assert.match(archive.title,/2025-01/);
  assert.match(archive.description,/2025-01/);
});
test('Password-protected resumes are noindex without publishing their details as schema', () => {
  for(const path of ['resume/index.html','resume-en/index.html']) {
    const meta=pageMetadata({...settings,page:{path,title:'Résumé',content:'Sensitive job details'}});
    assert.equal(meta.noindex,true);
    assert.equal(meta.schema,null);
    assert.doesNotMatch(meta.description,/Sensitive/);
    assert.match(metadataHtml(meta),/noindex, follow/);
  }
});
test('Sitemap contains unique canonical public routes with no synthetic timestamps', () => {
  const xml=sitemapXml(settings.origin,['index.html','en/index.html','resume/index.html','resume-en/index.html','design-history/index.html','design-history/main/index.html','en/index.html','tags/金融/index.html']);
  const $=load(xml,{xmlMode:true});
  assert.equal($('url').length,3);
  assert.equal($('lastmod').length,0);
  assert.match(xml,/%E9%87%91%E8%9E%8D/);
  assert.doesNotMatch(xml,/resume|design-history/);
});
test('English navigation and labels exist before JavaScript runs and preserve adjacent SVG icons', () => {
  const html='<html lang="en"><head></head><body><a data-en-label="Home" aria-label="首页"><span data-en="Sibo\'s Blog">中文</span><svg></svg></a></body></html>';
  const $=load(renderEnglishUi(html));
  assert.equal($('span').text(),"Sibo's Blog");
  assert.equal($('a').attr('aria-label'),'Home');
  assert.equal($('svg').length,1);
  const chinese=html.replace('lang="en"','lang="zh-CN"');
  assert.equal(renderEnglishUi(chinese),chinese);
});
