/* global hexo */
'use strict';
const { isPrivate } = require('../lib/site-seo');

// Analytics must not capture password-protected or private pages.
function publicAnalyticsEnabled() {
  const page = this.page || {};
  return !page.password && page.noindex !== true && page.sitemap !== false &&
    !isPrivate(String(page.path || '')) &&
    !isPrivate(String(page.canonical_path || ''));
}
hexo.extend.helper.register('clarity_enabled', publicAnalyticsEnabled);
hexo.extend.helper.register('public_analytics_enabled', publicAnalyticsEnabled);
