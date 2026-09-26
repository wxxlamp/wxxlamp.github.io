'use strict';
const { load } = require('cheerio');
function searchDocument(route, html) {
  const en = route.startsWith('en/');
  const local = route.replace(/^en\//, '');
  let kind;
  if (/^\d{4}\/\d{2}\/\d{2}\/.+\/index\.html$/.test(local)) kind = 'post';
  else if (/^(categories|tags)\/[^/]+\/index\.html$/.test(local)) kind = local.startsWith('tags/') ? 'tag' : 'category';
  else if (!en && /^resources\/(?:.*\/)?index\.html$/.test(local)) kind = 'resource';
  else if (!en && /^(about|subscribe)\/index\.html$/.test(local)) kind = 'page';
  else return null;
  const $ = load(html);
  if (($('meta[name="robots"]').attr('content') || '').includes('noindex')) return null;
  if (($('html').attr('lang') === 'en') !== en) return null;
  const title = $('h1').first().text().trim() || $('title').text().split(' - ')[0];
  const categories = $('.post-meta a').map((i, el) => $(el).text().trim()).get();
  const tags = $('.post-tags a').map((i, el) => $(el).text().trim()).get();
  $('script,style,noscript,.gutter,.resource-support').remove();
  const content = $('.post-content, .resource-file-summary, .resource-breadcrumb').clone();
  content.find('br').replaceWith(' ');
  content.find('p,div,li,pre,h1,h2,h3,h4,tr').append(' ');
  const body = content.text().replace(/\s+/g, ' ').trim();
  return { url: '/' + route.replace(/index\.html$/, ''), title, kind, categories, tags,
    description: $('meta[name="description"]').attr('content') || '', body };
}
module.exports = { searchDocument };
