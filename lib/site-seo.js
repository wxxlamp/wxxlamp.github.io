'use strict';
const { load } = require('cheerio');
const escape = (value = '') => String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
const cleanText = value => { const $ = load(String(value || ''), null, false); $('script,style').remove(); return $.text().replace(/\s+/g, ' ').trim(); };
const plainDescription = value => { const text = cleanText(value); return text.length > 180 ? text.slice(0, 177).trimEnd() + '…' : text; };
const canonicalUrl = (origin, path = '') => new URL(String(path).replace(/^\//, '').replace(/index\.html$/, ''), origin.replace(/\/?$/, '/')).href;
const isPrivate = path => /^(?:en\/)?(?:resume(?:-en)?|404|design-history)(?:\/|\.|$)/.test(path.replace(/^\//, ''));
function pageMetadata({ page, origin, language, siteTitle, author, taxonomyLabel }) {
  const en = language === 'en';
  const path = String(page.canonical_path || page.path || '').replace(/^\//, '').replace(/index\.html$/, '');
  const canonical = canonicalUrl(origin, path);
  const article = Boolean(page.__post || /^((en\/)?)\d{4}\/\d{2}\/\d{2}\//.test(path));
  const home = /^(en\/)?(page\/\d+\/)?$/.test(path);
  const about = /^(en\/)?about\/$/.test(path);
  const pageNumber = Number(page.current) || Number(path.match(/page\/(\d+)/)?.[1]) || 1;
  const baseDescription = en ? 'Sibo Wang writes about financial systems, AI agents, backend engineering, and life.' : '王星星的个人博客，分享金融系统、AI Agent、后端工程实践与生活思考。';
  let subject = cleanText(page.title);
  let description = page.description;
  if (home) { subject = en ? 'Financial Systems, AI Agents & Engineering' : '金融系统、AI Agent 与工程实践'; description = baseDescription; }
  else if (page.tag || page.category) {
    const label = taxonomyLabel(page.tag || page.category);
    const kind = page.tag ? (en ? 'Topic' : '话题') : (en ? 'Category' : '分类');
    subject = `${kind}: ${label}`;
    description = en ? `Browse the ${label} ${kind.toLowerCase()} on Sibo's Blog.` : `浏览「${label}」${kind}下的文章与实践记录。`;
  } else if (page.archive) {
    const period = [page.year, page.month ? String(page.month).padStart(2, '0') : ''].filter(Boolean).join('-');
    subject = (en ? 'Archive' : '文章归档') + (period ? ' · ' + period : '');
    description = en ? `Browse ${period || 'all'} articles by Sibo Wang on engineering and life.` : `按时间阅读王星星${period ? '在 ' + period + ' 发布的' : '的全部'}技术与生活文章。`;
  }
  if (pageNumber > 1) subject += en ? ` · Page ${pageNumber}` : ` · 第 ${pageNumber} 页`;
  description = plainDescription(description || (article ? page.excerpt || page.content : '') || baseDescription);
  const title = subject ? `${subject} | ${siteTitle}` : siteTitle;
  let image = canonicalUrl(origin, 'favicon.png');
  if (article) {
    const $ = load(page.content || '', null, false);
    const source = page.cover || page.thumbnail || $('img[src]').first().attr('src');
    try { if (source && /^(https?:|\/)/.test(source)) image = new URL(source, canonical).href; } catch {}
  }
  const noindex = isPrivate(path) || page.noindex === true || page.sitemap === false;
  const person = { '@type': 'Person', '@id': canonicalUrl(origin, 'about/#person'), name: author, url: canonicalUrl(origin, en ? 'en/about/' : 'about/') };
  const website = { '@type': 'WebSite', '@id': canonicalUrl(origin, (en ? 'en/' : '') + '#website'), name: siteTitle, url: canonicalUrl(origin, en ? 'en/' : ''), inLanguage: language };
  const entity = { '@type': article ? 'BlogPosting' : about ? 'AboutPage' : home || page.archive || page.tag || page.category ? 'CollectionPage' : 'WebPage', '@id': canonical + '#page', url: canonical, name: title, description, inLanguage: language, isPartOf: { '@id': website['@id'] } };
  if (about) entity.mainEntity = person;
  if (article) {
    entity.headline = cleanText(page.title);
    entity.author = person;
    entity.mainEntityOfPage = canonical;
    entity.image = [image];
    const date = page.date ? new Date(+page.date || page.date) : null;
    if (date && Number.isFinite(+date)) entity.datePublished = date.toISOString();
    const categories = Array.isArray(page.categories) ? page.categories : page.categories?.toArray?.() || [];
    if (categories.length) entity.articleSection = categories.map(c => taxonomyLabel(c.name || c));
  }
  return { path, title, description, canonical, image, language, siteTitle, author, article, noindex, schema: noindex ? null : { '@context': 'https://schema.org', '@graph': [website, entity] } };
}
function metadataHtml(meta) {
  const tag = (key, value, property = false) => `<meta ${property ? 'property' : 'name'}="${key}" content="${escape(value)}">`;
  const tags = [`<title>${escape(meta.title)}</title>`, `<link rel="canonical" href="${escape(meta.canonical)}">`, tag('description', meta.description), tag('author', meta.author), tag('robots', meta.noindex ? 'noindex, follow' : 'index, follow, max-image-preview:large'), tag('og:type', meta.article ? 'article' : 'website', true), tag('og:title', meta.title, true), tag('og:description', meta.description, true), tag('og:url', meta.canonical, true), tag('og:site_name', meta.siteTitle, true), tag('og:locale', meta.language === 'en' ? 'en_US' : 'zh_CN', true), tag('og:image', meta.image, true), tag('twitter:card', 'summary_large_image'), tag('twitter:title', meta.title), tag('twitter:description', meta.description), tag('twitter:image', meta.image)];
  if (meta.schema) tags.push('<script type="application/ld+json">' + JSON.stringify(meta.schema).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029') + '</script>');
  return tags.join('\n');
}
function sitemapXml(origin, paths) {
  const entries = [...new Set(paths)].filter(path => !isPrivate(path)).sort();
  return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries.map(path => `<url><loc>${escape(canonicalUrl(origin, path))}</loc></url>`).join('\n') + '\n</urlset>\n';
}
function renderEnglishUi(html) {
  const $ = load(html);
  if ($('html').attr('lang') !== 'en') return html;
  $('[data-en]').each((_, el) => $(el).text($(el).attr('data-en')));
  $('[data-en-label]').each((_, el) => $(el).attr('aria-label', $(el).attr('data-en-label')));
  return $.html();
}
module.exports = { pageMetadata, metadataHtml, sitemapXml, renderEnglishUi, canonicalUrl, isPrivate };
