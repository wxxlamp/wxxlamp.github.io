/* global hexo */
'use strict';
const { isPrivate } = require('../lib/site-seo');

// General analytics must not capture password-protected or private pages.
function publicAnalyticsEnabled() {
  const page = this.page || {};
  return !page.password && page.noindex !== true && page.sitemap !== false &&
    !isPrivate(String(page.path || '')) &&
    !isPrivate(String(page.canonical_path || ''));
}
hexo.extend.helper.register('clarity_enabled', publicAnalyticsEnabled);
hexo.extend.helper.register('public_analytics_enabled', publicAnalyticsEnabled);
// Only these two dedicated layouts may opt into resume stage analytics.
hexo.extend.helper.register('resume_analytics_page', function () {
  const page = this.page || {};
  return (page.layout === 'resume' && page.path === 'resume/index.html') ||
    (page.layout === 'resume-en' && page.path === 'resume-en/index.html');
});
