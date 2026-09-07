/* global hexo */
'use strict';

const highlight = hexo.extend.highlight.query('highlight.js');
hexo.extend.highlight.register('highlight.js', function (code, options) {
  // The blog's `shell` fences contain scripts/commands without console prompts.
  // highlight.js's shell grammar only highlights commands after a prompt.
  const lang = String(options.lang || '').toLowerCase();
  return highlight.call(this, code, { ...options, lang: lang === 'shell' ? 'bash' : lang });
});
