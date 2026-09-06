/* global hexo */
'use strict';
const { pageMetadata, metadataHtml, sitemapXml, renderEnglishUi } = require('../lib/site-seo');
const noindexPaths = new Set();
hexo.extend.filter.register('before_generate', () => noindexPaths.clear());
hexo.extend.filter.register('template_locals', locals => {
  if (locals.page.noindex === true || locals.page.sitemap === false) noindexPaths.add(locals.path);
  return locals;
});
hexo.extend.helper.register('seo_head', function () {
  return metadataHtml(pageMetadata({ page: this.page, origin: this.config.url, language: this.content_language(), siteTitle: this.site_title(), author: this.site_author(), taxonomyLabel: value => this.taxonomy_label(value) }));
});
hexo.extend.filter.register('after_render:html', renderEnglishUi);
hexo.extend.filter.register('after_generate', function () {
  const pages = this.route.list().filter(path => /\.html$/.test(path) && !noindexPaths.has(path));
  this.route.set('sitemap.xml', sitemapXml(this.config.url, pages));
  // Let crawlers read noindex on private/utility pages rather than blocking access.
  this.route.set('robots.txt', `User-agent: *\nAllow: /\n\nSitemap: ${this.config.url.replace(/\/$/, '')}/sitemap.xml\n`);
});
