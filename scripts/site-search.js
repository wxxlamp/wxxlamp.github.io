/* global hexo */
'use strict';
const { searchDocument } = require('../lib/site-search');
hexo.extend.filter.register('after_generate', async function () {
  const indexes = { zh: [], en: [] };
  for (const route of this.route.list().filter(route => route.endsWith('.html')).sort()) {
    // Only read candidate public content routes; resumes and snapshots never enter the index.
    if (!/^(?:en\/)?(?:\d{4}\/|categories\/|tags\/|resources\/|about\/|subscribe\/)/.test(route)) continue;
    let html = '';
    for await (const chunk of this.route.get(route)) html += chunk.toString();
    const entry = searchDocument(route, html);
    if (entry) indexes[route.startsWith('en/') ? 'en' : 'zh'].push(entry);
  }
  for (const language of ['zh', 'en']) this.route.set(`search/${language}.json`, JSON.stringify(indexes[language]));
}, 20);
