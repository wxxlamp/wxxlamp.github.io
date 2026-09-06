import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from wechat_layout import render
from wechat_links import link_label_issues, external_web_link
from editorial_quality import validate_html_fidelity, html_content, digest
from related_posts import candidates, validate_related
import pipeline


class ReadingLinksTest(unittest.TestCase):
    def test_repeated_links_have_one_copyable_reference(self):
        md='先看[幂等设计](https://example.com/a?x=1&y=2#scope)，再看[实现细节](https://example.com/a?x=1&y=2#scope)。'
        html=render(md)
        parsed=html_content(html)
        self.assertEqual([],parsed.links)
        self.assertEqual(1,''.join(parsed.text).count('https://example.com/a?x=1&y=2#scope'))
        self.assertEqual(3,''.join(parsed.text).count('[1]'))
        self.assertEqual([],validate_html_fidelity(md,html))
        self.assertGreater(pipeline.content_similarity(md,html,right_is_html=True),0.99)

    def test_exact_destinations_and_notes_are_verified(self):
        md='[资料](https://example.com/a#scope) 和 **已有判断**。'
        html=render(md)
        for modified in (html.replace('#scope','#other'),html.replace('已有判断','另一个结论'),html.replace('[1]','[2]',1),html.replace('https://example.com/a#scope','')):
            self.assertTrue(validate_html_fidelity(md,modified))

    def test_official_article_link_is_preserved_and_lookalike_is_not(self):
        self.assertFalse(external_web_link('https://mp.weixin.qq.com/s/actual-id'))
        self.assertTrue(external_web_link('https://mp.weixin.qq.com.example.org/s/fake'))
        self.assertTrue(external_web_link('https://mp.weixin.qq.com/login'))
        md='[公众号文章](https://mp.weixin.qq.com/s/actual-id) 与[网站](https://example.org)。'
        self.assertEqual(['https://mp.weixin.qq.com/s/actual-id'],html_content(render(md)).links)
        self.assertEqual([],validate_html_fidelity(md,render(md)))

    def test_reference_style_rich_label_images_and_code_survive(self):
        md='看[**架构**与 `API`][design]。\n\n[design]: https://example.com/design\n\n[![架构图](https://example.com/img.png)](https://example.com/article)\n\n```python\nurl = "https://example.com/code"\n```\n'
        self.assertEqual([],validate_html_fidelity(md,render(md)))
        self.assertEqual(['https://example.com/img.png'],html_content(render(md)).images)
        self.assertEqual(1,render(md).count('https://example.com/code'))

    def test_labels_must_be_meaningful_but_urls_in_code_are_not_labels(self):
        self.assertTrue(link_label_issues('[这里](https://example.com)'))
        self.assertTrue(link_label_issues('<https://example.com/long/url>'))
        self.assertTrue(link_label_issues('https://example.com/raw'))
        self.assertTrue(link_label_issues('资料在 https://example.com/long 页面。'))
        self.assertEqual([],link_label_issues('`https://example.com/code`\n\n![图](https://example.com/img)'))
        md='[明确主题](https://example.com/a)'
        self.assertEqual([],validate_html_fidelity(md,render(md,link_mode='inline')))


class RelatedPostsTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.env=patch.dict(os.environ,{'YMP_WORKSPACE_ROOT':str(self.root)});self.env.start();self.addCleanup(self.env.stop)
        (self.root/'_config.yml').write_text('url: https://blog.example\npermalink: :year/:month/:day/:title/\n')
        self.posts=self.root/'source/_posts';self.posts.mkdir(parents=True)
        for slug,extra,title in [('idempotency','','消息消费幂等设计'),('notes','','其他记录'),('future','date: 2099-01-01\n','未来幂等'),('private','password: secret\n','私有幂等'),('draft','published: false\n','草稿幂等')]:
            (self.posts/f'{slug}.md').write_text(f'---\ntitle: {title}\ndate: 2024-01-02\n{extra}---\n如何处理重复消费，需要幂等。')

    def test_search_ranks_relevant_titles_and_excludes_unpublished(self):
        result=candidates(self.root,['幂等'])['candidates']
        self.assertEqual('消息消费幂等设计',result[0]['title'])
        self.assertEqual(2,len(result))
        self.assertTrue(all(row['publication_status']=='needs-live-verification' for row in result))
        self.assertEqual([],candidates(self.root,['完全无关'])['candidates'])
        self.assertEqual(1,len(candidates(self.root,['幂等'],exclude='idempotency')['candidates']))

    def test_unknown_route_is_not_invented_and_english_requires_translation(self):
        self.assertEqual([],candidates(self.root,['幂等'],language='en')['candidates'])
        (self.root/'_config.yml').write_text('url: https://blog.example\npermalink: :unsupported/:title/\n')
        self.assertEqual([],candidates(self.root,['幂等'])['candidates'])

    def test_verified_selection_is_kept_in_both_channels_and_bound_to_source(self):
        row=candidates(self.root,['幂等'])['candidates'][0]
        project=self.root/'content-projects/new';(project/'draft').mkdir(parents=True);(project/'raw').mkdir()
        (project/'raw/source.md').write_text('新原稿讨论幂等。')
        row.update(relevance='解释略去的实现细节',placement='首次提及幂等处',label='幂等设计',publication_check={'status':'verified','url':row['url'],'checked_at':'2026-09-06','evidence':'测试页面身份与正文匹配'})
        plan={'queries':['幂等'],'source_sha256':digest(project/'raw/source.md'),'review_note':'选一篇有完整实现的旧文','selected':[row]}
        (project/'draft/related-posts.json').write_text(json.dumps(plan))
        for name in ('polished.md','wechat.md'):
            (project/'draft'/name).write_text('[幂等设计]('+row['url']+')')
        meta={'project':'new','related_posts_contract_version':1}
        self.assertEqual([],validate_related(project,self.root,meta,{'blog','wechat'}))
        (project/'draft/wechat.md').write_text('遗漏引用。')
        self.assertTrue(any('wechat.md 遗漏' in e for e in validate_related(project,self.root,meta,{'wechat'})))
        (self.posts/'idempotency.md').write_text('历史源文件变了')
        self.assertTrue(any('源文件已变化' in e for e in validate_related(project,self.root,meta,{'blog'})))

    def test_empty_selection_is_valid_but_missing_record_is_not(self):
        project=self.root/'content-projects/new';(project/'draft').mkdir(parents=True);(project/'raw').mkdir()
        (project/'raw/source.md').write_text('原稿')
        meta={'related_posts_contract_version':1}
        self.assertTrue(validate_related(project,self.root,meta,{'blog'}))
        (project/'draft/related-posts.json').write_text(json.dumps({'source_sha256':digest(project/'raw/source.md'),'queries':['新主题'],'selected':[],'review_note':'没有相关的已发表文章'}))
        self.assertEqual([],validate_related(project,self.root,meta,{'blog'}))
        self.assertEqual([],validate_related(project,self.root,{}, {'blog'}))

if __name__=='__main__':
    unittest.main()
