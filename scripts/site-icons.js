/* global hexo */
'use strict';
const paths = {
  'arrow-left': '<path d="m12 5-7 7 7 7M5 12h14"/>',
  'arrow-right': '<path d="m12 5 7 7-7 7M5 12h14"/>',
  'arrow-up': '<path d="m5 12 7-7 7 7M12 5v14"/>',
  external: '<path d="M7 17 17 7M7 7h10v10"/>',
  rss: '<path d="M5 10a9 9 0 0 1 9 9M5 4a15 15 0 0 1 15 15"/><circle cx="5" cy="19" r="1"/>',
  print: '<path d="M7 8V3h10v5M7 17H4V9h16v8h-3M7 14h10v7H7zM16 11h1"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  download: '<path d="M12 3v12m0 0 5-5m-5 5-5-5M5 21h14"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v16H6.5A2.5 2.5 0 0 0 4 21.5zm16 0A2.5 2.5 0 0 0 17.5 3H13v16h4.5a2.5 2.5 0 0 1 2.5 2.5z"/>'
};
hexo.extend.helper.register('site_icon', name => `<svg class="site-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${paths[name] || paths.external}</svg>`);
