'use strict';

// Explicit HTML content keeps article markup and code newlines intact in readers.
const { load } = require('cheerio');
function xml(value = '') {
  return String(value).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/g, '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}
function articleHtml(content, permalink) {
  const $ = load(content || '', null, false);
  $('script, iframe, .headerlink').remove();
  $('[href], [src], [poster]').each((_, el) => {
    for (const attr of ['href', 'src', 'poster']) {
      const value = $(el).attr(attr);
      if (!value || /^(mailto:|tel:|data:)/i.test(value)) continue;
      try { $(el).attr(attr, new URL(value, permalink).href); } catch (_) {}
    }
  });
  return $.html();
}
function feeds(posts, { url, title, description, author, language = 'zh-CN', prefix = '', limit = 20 }) {
  const base = new URL(prefix, url.replace(/\/?$/, '/')).href;
  const ordered = [...posts].sort((a, b) => +b.date - +a.date);
  const entries = limit ? ordered.slice(0, limit) : ordered;
  const iso = value => new Date(+value).toISOString();
  const updated = entries.length ? Math.max(...entries.map(p => +(p.updated || p.date))) : 0;
  const items = entries.map(p => ({ ...p, html: articleHtml(p.content, p.permalink) }));
  const atom = `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="${xml(language)}">
<title>${xml(title)}</title><subtitle>${xml(description)}</subtitle><id>${xml(base)}</id>
<link href="${xml(base)}" rel="alternate"/><link href="${xml(base + 'atom.xml')}" rel="self" type="application/atom+xml"/>
<icon>${xml(new URL('/favicon.ico', url).href)}</icon><updated>${iso(updated)}</updated><author><name>${xml(author)}</name></author>
${items.map(p => `<entry><title>${xml(p.title)}</title><id>${xml(p.permalink)}</id><link href="${xml(p.permalink)}"/><published>${iso(p.date)}</published><updated>${iso(p.updated || p.date)}</updated><summary type="text">${xml(p.description || '')}</summary><content type="html" xml:base="${xml(p.permalink)}">${xml(p.html)}</content></entry>`).join('\n')}
</feed>`;
  const rss = `<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
<title>${xml(title)}</title><description>${xml(description)}</description><link>${xml(base)}</link><language>${xml(language)}</language><lastBuildDate>${new Date(updated).toUTCString()}</lastBuildDate>
<atom:link href="${xml(base + 'rss.xml')}" rel="self" type="application/rss+xml"/>
${items.map(p => `<item><title>${xml(p.title)}</title><link>${xml(p.permalink)}</link><guid isPermaLink="true">${xml(p.permalink)}</guid><pubDate>${new Date(+p.date).toUTCString()}</pubDate><description>${xml(p.description || '')}</description><content:encoded>${xml(p.html)}</content:encoded></item>`).join('\n')}
</channel></rss>`;
  return [{ path: prefix + 'atom.xml', data: atom }, { path: prefix + 'rss.xml', data: rss }];
}
module.exports = { feeds, articleHtml };
