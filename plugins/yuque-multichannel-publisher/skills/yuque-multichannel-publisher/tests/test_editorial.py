import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial_quality import digest, validate_editorial, validate_series_evidence, validate_html_fidelity, without_fences
from wechat_layout import render
from style_profiles import author_prepare, command_author_save
from types import SimpleNamespace
import pipeline


class EditorialTest(unittest.TestCase):
    def test_renderer_preserves_symbols_code_links_images_table(self):
        md='# 1. 标题\n\n- **限制**：x != y，价格 9.9 元。\n- `a_b < 1`\n\n[文档](https://example.com/docs)\n\n![截图](https://example.com/img.png)\n\n> 只验证过此情况。\n\n```python\nif x != 2:\n    print("好")\n```\n\n|方案|限制|\n|---|---|\n|A|1 < 2|\n'
        for theme in ('ink','warm'):
            html=render(md,theme)
            self.assertEqual([],validate_html_fidelity(md,html))
            self.assertNotIn('<style',html)
            self.assertTrue(validate_html_fidelity(md,html.replace('9.9','9.8')))
            self.assertTrue(validate_html_fidelity(md,html.replace('    print','print')))
            self.assertTrue(validate_html_fidelity(md,html.replace('example.com/docs','example.com/other')))
            self.assertTrue(validate_html_fidelity(md,html.replace('example.com/img.png','example.com/other.png')))

    def test_raw_html_is_not_silently_lost(self):
        for md in ('<div>原始材料</div>', '正文 <span>材料</span>。'):
            with self.assertRaises(ValueError):
                render(md)

    def test_fenced_headings_are_not_sections(self):
        md='# 1. 正文\n```bash\n# 这只是注释\n```\n~~~md\n# 这也是代码\n~~~\n'
        self.assertEqual(['1. 正文'],pipeline.H1_RE.findall(without_fences(md)))

    def plan(self):
        return {'content_units':[{'id':'u1','source_excerpt':'检查采光'}, {'id':'u2','source_excerpt':'确认费用'}],
                'rounds':[{'round':'round1','unit_ids':['u1'],'split_reason':'看房时使用','standalone_test':'交代看房对象和检查步骤','overlap_review':'仅共用城市背景'},
                          {'round':'round2','unit_ids':['u2'],'split_reason':'签约时使用','standalone_test':'独立交代费用项目','overlap_review':'只共用必要背景'}]}

    def test_series_split_merge_and_evidence(self):
        plan=self.plan()
        self.assertEqual([],validate_series_evidence(plan,'先检查采光，再确认费用。'))
        plan['rounds'][1]['unit_ids']=['u1']
        errors=validate_series_evidence(plan,'先检查采光，再确认费用。')
        self.assertTrue(any('完全相同' in x for x in errors))
        self.assertTrue(any('未分配' in x for x in errors))
        plan['rounds']=plan['rounds'][:1]
        plan['rounds'][0]['unit_ids']=['u1','u2']
        self.assertEqual([],validate_series_evidence(plan,'先检查采光，再确认费用。'))
        self.assertTrue(validate_series_evidence(plan,'不存在的材料'))

    def test_v2_review_is_required_and_stale_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ,{'YMP_WORKSPACE_ROOT':t}):
            project=Path(t)/'content-projects/demo'
            (project/'draft').mkdir(parents=True)
            (project/'raw').mkdir()
            (project/'draft/polished.md').write_text('确定的内容。')
            (project/'raw/source.md').write_text('原稿内容。')
            self.assertTrue(validate_editorial(project,{}, {'blog'}))
            report={'status':'passed','voice_mode':'cold-start','voice_limitation':'没有历史样本',
                    'artifacts':{n:digest(project/n) for n in ('raw/source.md','draft/polished.md')},
                    'reviews':{'polished':{k:'已逐句检查，具体内容未作扩展' for k in ('voice','naturalness','typos','format','facts')}},
                    'fact_checks':[],'fact_scope':'仅编辑给定作者自述，没有外部事实'}
            (project/'draft/editorial-review.json').write_text(json.dumps(report))
            self.assertEqual([],validate_editorial(project,{}, {'blog'}))
            (project/'draft/polished.md').write_text('修改后的内容。')
            self.assertTrue(any('过期' in e for e in validate_editorial(project,{}, {'blog'})))

    def test_knowledge_errors_and_time_sensitive_claims_block(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ,{'YMP_WORKSPACE_ROOT':t}):
            project=Path(t)
            (project/'draft').mkdir()
            report={'status':'passed','fact_checks':[{'claim':'当前价格','status':'pending'}]}
            (project/'draft/editorial-review.json').write_text(json.dumps(report))
            self.assertTrue(any('待确认' in e for e in validate_editorial(project,{},set())))
            report['fact_checks']=[{'claim':'当前价格','status':'verified','time_sensitive':True,'basis':'猜测','location':'第二段'}]
            (project/'draft/editorial-review.json').write_text(json.dumps(report))
            self.assertTrue(any('权威来源' in e for e in validate_editorial(project,{},set())))

    def test_author_cache_reuse_incremental_and_generated_exclusion(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ,{'YMP_WORKSPACE_ROOT':t}):
            root=Path(t)
            posts=root/'source/_posts';posts.mkdir(parents=True)
            for name in ('one','two','three','generated'):
                (posts/f'{name}.md').write_text(f'---\ntitle: {name}\ncategories: 技术\n---\n{name} 正文')
            project=root/'content-projects/generated';project.mkdir(parents=True)
            (project/'metadata.json').write_text('{"project":"generated"}')
            first=author_prepare(root)
            self.assertEqual('learn',first['action'])
            self.assertFalse(any('generated' in p for p in first['read_samples']))
            profile=root/'input.md';profile.write_text('第一人称直接叙述。')
            command_author_save(SimpleNamespace(input=str(profile),samples=first['read_samples']))
            self.assertEqual([],author_prepare(root)['read_samples'])
            self.assertEqual('reuse',author_prepare(root)['action'])
            (posts/'one.md').write_text('修改后的文章')
            self.assertEqual('refresh',author_prepare(root)['action'])

    def test_content_driven_images_and_code_heading(self):
        with tempfile.TemporaryDirectory() as t:
            project=Path(t);(project/'draft').mkdir()
            (project/'draft/polished.md').write_text('![首图](https://example.com/a.png)\n\n# 1. 引言\n\n短引言不需要配图。\n\n```bash\n# comment\n```\n')
            metadata={'title':'标题','description':'描述','channels':['blog'],'section_image_policy':'content-driven',
                      'cover_image':{'url':'https://example.com/a.png','ratio':'21:9','style':'ghibli-inspired'}}
            self.assertEqual([],pipeline.validate_draft(project,metadata)[0])

    def test_v2_materialization_and_published_file_drift(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ,{'YMP_WORKSPACE_ROOT':t}):
            root=Path(t).resolve()
            pipeline.command_init(SimpleNamespace(project='review-demo',yuque_url='https://www.yuque.com/a/b/c',title='排版测试',edit_mode='correction-only',channels=['blog']))
            project=pipeline.project_dir(root,'review-demo')
            metadata=pipeline.read_json(project/'metadata.json')
            metadata.pop('publishing_contract_version', None)  # Existing editorial-v2 projects stay compatible.
            metadata.update({'description':'用于验证经过审阅的内容能完整落盘。','cover_image':{'url':'https://example.com/cover.png','ratio':'21:9','style':'ghibli-inspired'}})
            source='![首图](https://example.com/cover.png)\n\n# 1. 记录\n\n这是作者已有的一段自述。\n'
            (project/'draft/polished.md').write_text(source)
            (project/'raw/source.md').write_text(source)
            pipeline.atomic_json(project/'metadata.json',metadata)
            report={'status':'passed','voice_mode':'cold-start','voice_limitation':'测试中没有历史样本',
                    'artifacts':{n:digest(project/n) for n in ('raw/source.md','draft/polished.md')},
                    'reviews':{'polished':{k:'检查给定自述，未新增内容' for k in ('voice','naturalness','typos','format','facts')}},
                    'fact_checks':[],'fact_scope':'仅作者自述'}
            (project/'draft/editorial-review.json').write_text(json.dumps(report))
            state=pipeline.read_json(pipeline.state_path(project))
            state['current_stage']='reviewed'
            pipeline.atomic_json(pipeline.state_path(project),state)
            pipeline.command_materialize(SimpleNamespace(project='review-demo',allow_incomplete=False))
            self.assertEqual([],pipeline.validate_materialized(root,'review-demo',metadata)[0])
            target=pipeline.expected_outputs(root,'review-demo')['blog']
            target.write_text(target.read_text().replace('已有','虚构'))
            self.assertTrue(any('不一致' in e for e in pipeline.validate_materialized(root,'review-demo',metadata)[0]))

if __name__=='__main__':
    unittest.main()
