/* global hexo */
'use strict';
const { isPrivate } = require('../lib/site-seo');

// Session recordings must not capture password-protected or private pages.
hexo.extend.helper.register('clarity_enabled', function () {
  const page = this.page || {};
  return !page.password && page.noindex !== true && page.sitemap !== false &&
    !isPrivate(String(page.path || '')) &&
    !isPrivate(String(page.canonical_path || ''));
});
