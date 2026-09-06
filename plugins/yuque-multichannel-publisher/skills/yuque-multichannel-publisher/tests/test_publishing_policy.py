import copy
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline
from editorial_quality import digest, required_artifacts, validate_editorial
from publishing_policy import catalog_context, validate_plan, title_for
from reference_links import reference_context
import yaml


class PublishingPolicyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.env = patch.dict(os.environ, {'YMP_WORKSPACE_ROOT': str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        catalog = self.root / 'source/_data/taxonomy.json'
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({'categories': [{'zh': '基础夯实', 'en': 'Foundations'}], 'topics': [{'id': 'jvm', 'zh': 'Java 虚拟机', 'en': 'JVM'}]}))
        with redirect_stdout(StringIO()):
            pipeline.command_init(SimpleNamespace(project='demo', yuque_url='https://www.yuque.com/a/b/c', title='原始标题', edit_mode='correction-only', channels=['blog']))
        self.project = pipeline.project_dir(self.root, 'demo')
        self.metadata = pipeline.read_json(self.project / 'metadata.json')
        self.metadata.update(description='解释 Java 内存分配方式与使用限制。', cover_image={'url': 'https://example.com/zh.png', 'ratio': '21:9', 'style': 'ghibli-inspired'})
        self.source = '![首图](https://example.com/zh.png)\n\n# 1. 内存分配\n\n解释分配方式和限制。\n\n[文档](https://example.com/docs)\n\n```java\nint x = 1;\n```\n'
        (self.project / 'draft/polished.md').write_text(self.source)
        (self.project / 'raw/source.md').write_text(self.source)
        pipeline.atomic_json(self.project/'draft/related-posts.json', {'source_sha256':digest(self.project/'raw/source.md'),'queries':['Java 内存分配'],'selected':[],'review_note':'测试工作区没有已发表文章，不附加推荐'})
        self.plan = {'version': 1, 'references_sha256': reference_context(self.root)['sha256'], 'references_review': {'zh': '检查中文来源和可用语言', 'en': '检查英文来源及原始资料，测试无站内链接'}, 'source_sha256': digest(self.project / 'draft/polished.md'),
                     'titles': {'blog': {'text': 'Java 内存分配：机制与限制', 'reason': '明确技术对象与内容范围'}, 'wechat': {'text': 'Java 对象到底放在哪？从一次分配说起', 'reason': '用正文解释的问题吸引读者'}},
                     'taxonomy': {'catalog_sha256': catalog_context(self.root)['catalog_sha256'], 'categories': ['基础夯实'], 'topics': ['Java 虚拟机'], 'reason': '正文讨论 JVM 内存分配'},
                     'english': {'decision': 'skip', 'reason': '当前示例仅供本地课程记录，尚不具备完整论证'}}
        self.save()

    def save(self):
        pipeline.atomic_json(self.project / 'metadata.json', self.metadata)
        pipeline.atomic_json(self.project / 'draft/publishing-plan.json', self.plan)

    def errors(self):
        self.save()
        return validate_plan(self.project, self.metadata, self.root)

    def english(self):
        self.plan['english'] = {'decision': 'generate', 'reason': '可复用的内存模型解释与工程限制', 'audience': 'Java backend engineers', 'title': 'Java Memory Allocation: Mechanisms and Limits', 'description': 'How Java allocates memory and where its constraints matter.',
                                'images': [{'source_url': 'https://example.com/zh.png', 'url': 'https://example.com/en.png', 'language': 'en', 'review_status': 'passed', 'review_note': 'Checked every English diagram label against the source.'}]}
        (self.project / 'draft/english.md').write_text('![Cover](https://example.com/en.png)\n\n# 1. Memory Allocation\n\nAn explanation of memory allocation mechanisms and their practical constraints.\n\n[Documentation](https://example.com/docs)\n\n```java\nint x = 1;\n```\n')
        self.save()

    def review(self):
        self.save()
        targets = ['polished'] + (['english'] if self.plan['english']['decision'] == 'generate' else [])
        report = {'status': 'passed', 'voice_mode': 'cold-start', 'voice_limitation': '测试没有历史样本',
                  'artifacts': {n: digest(self.project/n) for n in required_artifacts(self.project, {'blog'})},
                  'reviews': {target: {field: '检查给定原稿与技术示例，保留事实和限制' for field in ('voice', 'naturalness', 'typos', 'format', 'facts')} for target in targets},
                  'fact_checks': [], 'fact_scope': '测试固定输入，不新增外部事实'}
        pipeline.atomic_json(self.project/'draft/editorial-review.json', report)
        state = pipeline.read_json(pipeline.state_path(self.project))
        state['current_stage'] = 'reviewed'
        pipeline.atomic_json(pipeline.state_path(self.project), state)

    def materialize(self):
        with redirect_stdout(StringIO()):
            pipeline.command_materialize(SimpleNamespace(project='demo', allow_incomplete=False))
        return pipeline.expected_outputs(self.root, 'demo')

    def test_channel_titles_and_canonical_taxonomy(self):
        self.assertEqual([], self.errors())
        self.assertNotEqual(title_for(self.project, self.metadata, 'blog'), title_for(self.project, self.metadata, 'wechat'))
        self.plan['taxonomy']['topics'] = ['JVM']
        self.assertTrue(any('规范' in e or '中文名称' in e for e in self.errors()))
        self.plan['taxonomy']['topics'] = ['Java 虚拟机']
        self.plan['taxonomy']['catalog_sha256'] = 'stale'
        self.assertTrue(any('目录已变化' in e for e in self.errors()))

    def test_title_review_and_selection_required(self):
        self.plan['titles']['blog']['text'] = '震惊！必看的 Java 内存'
        self.assertTrue(any('营销' in e for e in self.errors()))
        self.plan['english'] = {}
        self.assertTrue(any('明确决策' in e for e in self.errors()))
        self.plan['english'] = []
        self.assertTrue(self.errors())
        self.assertNotIn('draft/english.md', required_artifacts(self.project, {'blog'}))

    def test_skip_materializes_only_chinese_and_blocks_stale_english(self):
        self.review()
        out = self.materialize()
        self.assertFalse(out['blog_en'].exists())
        meta = yaml.safe_load(out['blog'].read_text().split('---')[1])
        self.assertEqual(self.plan['titles']['blog']['text'], meta['title'])
        self.assertEqual(['Java 虚拟机'], meta['tags'])
        original = out['blog'].read_text()
        out['blog_en'].parent.mkdir(parents=True)
        out['blog_en'].write_text('Existing translation must not be silently deleted.')
        with self.assertRaises(SystemExit): self.materialize()
        self.assertEqual(original, out['blog'].read_text())

    def test_english_pair_materialization_and_stale_review(self):
        self.english()
        self.assertEqual([], self.errors())
        self.review()
        out = self.materialize()
        a = yaml.safe_load(out['blog'].read_text().split('---')[1])
        b = yaml.safe_load(out['blog_en'].read_text().split('---')[1])
        self.assertEqual('en', b['lang'])
        self.assertEqual('demo', b['translation_of'])
        for key in ('date', 'tags', 'categories'): self.assertEqual(a[key], b[key])
        self.assertEqual([], pipeline.validate_materialized(self.root, 'demo', self.metadata)[0])
        self.plan['titles']['blog']['text'] += '与边界'
        self.save()
        self.assertTrue(any('过期' in e for e in validate_editorial(self.project, self.metadata, {'blog'})))
        out['blog_en'].write_text(out['blog_en'].read_text() + '\nUnreviewed text.')
        self.assertTrue(pipeline.validate_materialized(self.root, 'demo', self.metadata)[0])

    def test_english_images_need_real_translation_or_no_text_review(self):
        self.english()
        self.plan['english']['images'] = []
        self.assertTrue(any('覆盖全部' in e for e in self.errors()))
        self.english()
        self.plan['english']['images'][0]['url'] = 'https://example.com/zh.png'
        target = self.project/'draft/english.md'
        target.write_text(target.read_text().replace('/en.png', '/zh.png'))
        self.assertTrue(any('独立英文版' in e for e in self.errors()))
        self.plan['english']['images'][0]['language'] = 'no-text'
        self.assertEqual([], self.errors())

    def test_translation_preserves_code_structure_and_citations(self):
        self.english()
        target = self.project/'draft/english.md'
        target.write_text(target.read_text().replace('int x = 1;', 'int x = 2;').replace('# 1.', '## 1.').replace('https://example.com/docs', 'https://example.com/other'))
        errors = self.errors()
        for part in ('代码块', '章节层级', '引用链接'): self.assertTrue(any(part in e for e in errors))

    def test_social_only_does_not_require_blog_taxonomy_or_english(self):
        self.metadata['channels'] = ['wechat']
        del self.plan['taxonomy']
        del self.plan['english']
        self.assertEqual([], self.errors())

if __name__ == '__main__': unittest.main()
