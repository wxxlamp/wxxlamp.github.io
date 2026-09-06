/* global hexo */
'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const frontMatter = require('hexo-front-matter');
const pagination = require('hexo-pagination');
const { feeds } = require('../lib/blog-feeds');
const { load } = require('cheerio');
let translated = new Map();
let englishRoutes = new Set(['en/', 'en/about/', 'en/subscribe/', 'en/atom.xml', 'en/rss.xml']);
const normalize = value => String(value || '').replace(/^\//, '').replace(/index\.html$/, '');
const isEnglish = page => page.lang === 'en' || page.layout === 'resume-en' || normalize(page.path).startsWith('en/');
const taxonomy = require('../source/_data/taxonomy.json');
const taxonomyLabels = Object.fromEntries([...taxonomy.categories, ...taxonomy.topics].map(item => [item.zh, item.en]));
hexo.extend.helper.register('taxonomy_label', function (name) { return isEnglish(this.page) ? taxonomyLabels[name] || name : name; });
hexo.extend.helper.register('site_title', function () { return isEnglish(this.page) ? "Sibo's Blog" : this.config.title; });
hexo.extend.helper.register('site_author', function () { return isEnglish(this.page) ? 'Sibo Wang' : '王星星'; });
hexo.extend.helper.register('site_description', function () { return isEnglish(this.page) ? 'Engineering, reading, and life.' : this.config.description; });

hexo.extend.helper.register('localized_post_count', function () { return isEnglish(this.page) ? translated.size : this.site.posts.length; });
hexo.extend.helper.register('content_language', function () { return isEnglish(this.page) ? 'en' : 'zh-CN'; });
hexo.extend.helper.register('localized_path', function (value) {
  const target = normalize(value);
  return this.url_for(isEnglish(this.page) && englishRoutes.has('en/' + target) ? 'en/' + target : target);
});
hexo.extend.helper.register('language_url', function (language) {
  const current = normalize(this.page.path || this.path);
  if (/^resume(-en)?\/$/.test(current)) return this.url_for(language === 'en' ? 'resume-en/' : 'resume/');
  const chinese = current.replace(/^en\//, '');
  if (language === 'zh') return this.url_for(chinese);
  return englishRoutes.has('en/' + chinese) ? this.url_for('en/' + chinese) : '';
});
hexo.extend.helper.register('translation_url', function (post) {
  if (post.lang === 'en') return this.url_for(post.original_path);
  const entry = translated.get(post.slug);
  return entry ? this.url_for(entry.path) : '';
});
hexo.extend.helper.register('localized_taxonomy', function (kind) {
  const en = isEnglish(this.page);
  return this.site[kind].toArray().map(item => ({
    name: item.name,
    count: en ? [...translated.values()].filter(post => post[kind].some(t => t.name === item.name)).length : item.posts.length,
    path: (en ? 'en/' : '') + item.path
  })).filter(item => item.count > 0).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-CN'));
});

// Replace the plugin's output to preserve HTML type and code whitespace.
hexo.extend.generator.register('atom', () => []);
hexo.extend.generator.register('rss2', () => []);
hexo.extend.generator.register('localized-content', async function (locals) {
  const originals = locals.posts.toArray().filter(p => !p.source.startsWith('_posts/en/'));
  const byFilename = new Map(originals.map(p => [path.basename(p.source, '.md'), p]));
  const dir = path.join(this.source_dir, '_posts/en');
  const names = await fs.readdir(dir).catch(error => { if (error.code === 'ENOENT') return []; throw error; });
  const english = [];
  translated = new Map();
  englishRoutes = new Set(['en/', 'en/about/', 'en/subscribe/', 'en/atom.xml', 'en/rss.xml']);
  for (const name of names.filter(n => n.endsWith('.md')).sort()) {
    const document = frontMatter.parse(await fs.readFile(path.join(dir, name), 'utf8'));
    const original = byFilename.get(document.translation_of || path.basename(name, '.md'));
    if (!original) throw new Error(`English translation has no original: ${name}`);
    if (document.lang !== 'en' || !document.title || !document._content.trim()) throw new Error(`Incomplete English translation: ${name}`);
    const route = 'en/' + original.path;
    let content = await this.render.render({ text: document._content, engine: 'markdown', path: path.join(dir, name) });
    // Keep source heading IDs so existing section links work in either language.
    let sourceHtml = load(original.content, null, false);
    const englishHtml = load(content, null, false);
    let sourceHeadings = sourceHtml('h1,h2,h3,h4,h5,h6').toArray();
    const englishHeadings = englishHtml('h1,h2,h3,h4,h5,h6').toArray();
    if (sourceHeadings.length !== englishHeadings.length) {
      // Older posts sometimes place headings immediately after raw HTML. Read
      // their Markdown headings separately so the English page still has stable IDs.
      const source = frontMatter.parse(await fs.readFile(path.join(this.source_dir, original.source), 'utf8'));
      const headings = source._content.replace(/^\s*(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\s*\1\s*$/gm, '')
        .split('\n').filter(line => /^#{1,6}\s/.test(line)).join('\n\n');
      sourceHtml = load(await this.render.render({ text: headings, engine: 'markdown' }), null, false);
      sourceHeadings = sourceHtml('h1,h2,h3,h4,h5,h6').toArray();
    }
    if (sourceHeadings.length !== englishHeadings.length) throw new Error(`Translation heading mismatch: ${name}`);
    if (sourceHeadings.length === englishHeadings.length) {
      englishHeadings.forEach((element, i) => {
        const id = sourceHtml(sourceHeadings[i]).attr('id');
        if (id) { englishHtml(element).attr('id', id); englishHtml(element).find('.headerlink').attr('href', '#' + id); }
      });
      content = englishHtml.html();
    }
    const post = {
      title: document.title, description: document.description || '', content,
      date: original.date, updated: original.updated, slug: original.slug,
      path: route, canonical_path: route, permalink: new URL(route, this.config.url + '/').href,
      original_path: original.path, lang: 'en', __post: true, layout: 'post',
      categories: original.categories.toArray().map(c => ({ name: c.name, path: 'en/' + c.path })),
      tags: original.tags.toArray().map(t => ({ name: t.name, path: 'en/' + t.path }))
    };
    english.push(post); translated.set(original.slug, post); englishRoutes.add(normalize(route));
  }
  english.sort((a, b) => +b.date - +a.date);
  const routes = english.map((post, i) => {
    post.prev = english[i - 1]; post.next = english[i + 1];
    return { path: post.path, layout: 'post', data: post };
  });
  const addPages = (base, posts, data, perPage, layout) => {
    const pages = pagination(base, posts, { perPage, layout, data: { ...data, lang: 'en' } });
    pages.forEach(page => englishRoutes.add(normalize(page.path)));
    routes.push(...pages);
  };
  addPages('en/', english, { __index: true }, this.config.index_generator.per_page, 'index');
  addPages('en/archives/', english, { archive: true }, 0, 'archive');
  const years = new Set(english.map(post => post.date.format('YYYY')));
  for (const year of years) {
    const yearPosts = english.filter(post => post.date.format('YYYY') === year);
    addPages('en/archives/' + year + '/', yearPosts, { archive: true, year: Number(year) }, 0, 'archive');
    for (const month of new Set(yearPosts.map(post => post.date.format('MM')))) {
      addPages('en/archives/' + year + '/' + month + '/', yearPosts.filter(post => post.date.format('MM') === month),
        { archive: true, year: Number(year), month: Number(month) }, 0, 'archive');
    }
  }
  for (const kind of ['categories', 'tags']) {
    for (const item of locals[kind].toArray()) {
      const posts = english.filter(p => p[kind].some(t => t.name === item.name));
      if (!posts.length) continue;
      addPages('en/' + item.path, posts, { [kind === 'tags' ? 'tag' : 'category']: item.name }, 0, 'archive');
    }
  }
  const settings = { url: this.config.url, title: this.config.title, description: this.config.description, author: this.config.author, limit: this.config.feed.limit };
  routes.push(...feeds(originals, settings));
  routes.push(...feeds(english, { ...settings, prefix: 'en/', language: 'en', author: 'Sibo Wang', title: "Sibo's Blog", description: 'Engineering, reading, and life.' }));
  this.log.info('Local English translations: %d / %d', english.length, originals.length);
  return routes;
});
