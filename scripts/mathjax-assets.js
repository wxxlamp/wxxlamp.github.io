/* global hexo */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
hexo.extend.generator.register('mathjax-assets', function () {
  const base = path.join(path.dirname(require.resolve('mathjax/package.json')), 'es5');
  const routes = [];
  function visit(dir, prefix = '') {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const relative = prefix + entry.name;
      if (entry.isDirectory()) visit(path.join(dir, entry.name), relative + '/');
      else if (/\.(js|woff)$/.test(entry.name)) routes.push({ path: 'lib/mathjax/' + relative, data: () => fs.createReadStream(path.join(base, relative)) });
    }
  }
  visit(base);
  return routes;
});
