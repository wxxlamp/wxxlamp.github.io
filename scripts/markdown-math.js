/* global hexo */
'use strict';
const { extensions } = require('../lib/markdown-math');
hexo.extend.filter.register('marked:extensions', list => list.push(...extensions));
