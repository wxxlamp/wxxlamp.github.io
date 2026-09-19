/* global hexo */
'use strict';

const manifest = require('../source/_data/hkust-resources.json');

function sectionItems(section) {
  if (section.items) return section.items;
  return section.groups.reduce((items, group) => items.concat(group.items), []);
}

hexo.extend.generator.register('hkust-resource-pages', function (locals) {
  const items = manifest.sections.reduce((all, section) => {
    return all.concat(sectionItems(section).map(item => Object.assign({ course: section.title }, item)));
  }, []);

  return items.filter(item => item.kind === 'pdf' || item.post).map((item) => {
    const index = items.findIndex(candidate => candidate.id === item.id);
    const summary = item.kind === 'pdf'
      ? `${item.course}《${item.title}》，共 ${item.pages} 页，可在线预览或下载 PDF 原文件。`
      : `${item.course}延伸阅读：《${item.title}》。`;
    const data = {
      layout: 'resource-doc',
      title: item.title,
      seo_title: `${item.title} · ${item.course} · HKUST 历史资料`,
      description: summary,
      resource_id: item.id,
      resource_kind: item.kind,
      resource_course: item.course,
      resource_file: item.file,
      resource_pages: item.pages,
      resource_summary: summary,
      resource_original: item.post ? `/${item.post}/` : item.file,
      resource_previous: index > 0 ? items[index - 1] : null,
      resource_next: index < items.length - 1 ? items[index + 1] : null
    };

    if (item.kind === 'markdown') {
      const post = locals.posts.findOne({ slug: item.post });
      if (!post) {
        hexo.log.warn(`Resource source post not found: ${item.post}`);
        data.content = '<p>文章暂时无法载入。</p>';
      } else {
        data.content = post.content;
        data.description = post.description || data.description;
        data.date = post.date;
        data.updated = post.updated;
        data.resource_original = `/${post.path}`;
        data.resource_summary = null;
      }
    }

    return {
      path: item.href.replace(/^\//, '') + 'index.html',
      layout: 'resource-doc',
      data
    };
  });
});
