import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline
from editorial_quality import digest, required_artifacts, validate_editorial


class BodyImagesTest(unittest.TestCase):
    def record(self, url, section='1. 流程'):
        return dict(url=url, section=section, ratio='16:9', section_claim='先查询，再处理',
                    visual_type='process-diagram', must_show=['查询', '处理'], avoid=['伪代码'],
                    prompt='清楚展示查询与处理的顺序', placement_reason='放在相关步骤说明后',
                    review_status='passed')

    def test_legacy_and_new_projects_allow_zero_generated_images(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ, {'YMP_WORKSPACE_ROOT': t}):
            project=Path(t); (project/'draft').mkdir()
            body='![首图](https://example.com/cover.png)\n\n# 1. 引言\n\n短引言。\n\n# 2. 操作\n\n![已有竖向截图][screen]\n\n# 3. 结语\n\n结束。\n\n[screen]: https://example.com/screenshot.png\n'
            (project/'draft/polished.md').write_text(body)
            metadata=dict(title='标题', description='描述', channels=['blog'], cover_image=dict(url='https://example.com/cover.png',ratio='21:9',style='ghibli-inspired'))
            for policy in (None, 'content-driven', 'one-per-section'):
                if policy is not None: metadata['section_image_policy']=policy
                self.assertEqual([],pipeline.validate_draft(project,metadata)[0])

    def test_multiple_images_in_one_section_and_shared_parent_image(self):
        a,b='https://example.com/a.png','https://example.com/b.png'
        body=f'# 1. 流程\n\n先看总体关系。\n\n![整体]({a})\n\n## 1.1. 查询\n\n查询说明。\n\n## 1.2. 处理\n\n处理说明。\n\n![细节][detail]\n\n[detail]: {b}\n'
        metadata={'section_images': {'overview':self.record(a),'detail':self.record(b,'1.2. 处理')}}
        self.assertEqual([],pipeline.validate_body_images(body,metadata))
        metadata['section_images']['detail']['section']='1. 流程'
        self.assertEqual([],pipeline.validate_body_images(body,metadata))
        metadata['section_images']['detail']['section']='1.1. 查询'
        self.assertTrue(any('指定章节' in e for e in pipeline.validate_body_images(body,metadata)))

    def test_no_heading_and_existing_html_images(self):
        url='https://example.com/a.png'
        body=f'一段叙事。\n\n<img src="{url}" alt="具体场景">\n\n继续叙事。'
        self.assertEqual([],pipeline.validate_body_images(body,{'section_images':{'scene':self.record(url,'')}}))

    def test_wrong_missing_duplicate_and_unreviewed_images_rejected(self):
        url='https://example.com/a.png'; body=f'# 1. 流程\n\n![流程]({url})'
        for change in ({'url':'https://example.com/missing.png'},{'section':'2. 不存在'}, {'review_status':'pending'}, {'placement_reason':''}):
            with self.subTest(change=change):
                record={**self.record(url),**change}
                self.assertTrue(pipeline.validate_body_images(body,{'section_images':{'flow':record}}))
        record=self.record(url)
        self.assertTrue(any('重复登记' in e for e in pipeline.validate_body_images(body,{'section_images':{'a':record,'b':record}})))

    def test_markdown_image_inside_code_does_not_count(self):
        url='https://example.com/a.png'
        for code in (f'```md\n![伪图]({url})\n```',f'    ![伪图]({url})',f'`![伪图]({url})`'):
            with self.subTest(code=code):
                self.assertTrue(pipeline.validate_body_images('# 1. 流程\n\n'+code,{'section_images':{'flow':self.record(url)}}))

    def test_upload_keeps_brief_and_other_slot_but_invalidates_old_approval(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ, {'YMP_WORKSPACE_ROOT': t}):
            project=Path(t); file=project/'flow.png'; file.write_bytes(b'mocked image')
            first=self.record('https://example.com/old.png')
            second=self.record('https://example.com/second.png')
            metadata={'section_images': {'flow':first, 'detail':second}}
            args=SimpleNamespace(project='demo',file=str(file),kind='section',key='flow',provider=None,style=None)
            result=SimpleNamespace(returncode=0,stdout='',stderr='')
            with patch.object(pipeline,'find_workspace_root',return_value=project), patch.object(pipeline,'load_project',return_value=(project,{},metadata)), patch.object(pipeline,'require_image_ratio',return_value=(1600,900)), patch.object(pipeline.subprocess,'run',return_value=result), patch.object(pipeline,'parse_uploaded_url',return_value='https://example.com/new.png'), patch.object(pipeline,'atomic_json'), patch.object(pipeline,'append_event'):
                pipeline.command_upload_image(args)
            self.assertEqual('https://example.com/new.png',metadata['section_images']['flow']['url'])
            self.assertEqual(first['prompt'],metadata['section_images']['flow']['prompt'])
            self.assertEqual(first['section'],metadata['section_images']['flow']['section'])
            self.assertEqual('pending',metadata['section_images']['flow']['review_status'])
            self.assertEqual(second,metadata['section_images']['detail'])

    def test_changed_visual_plan_requires_new_editorial_review(self):
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ, {'YMP_WORKSPACE_ROOT': t}):
            project=Path(t); (project/'draft').mkdir(); (project/'raw').mkdir()
            (project/'raw/source.md').write_text('原稿')
            (project/'draft/polished.md').write_text('正文')
            plan=project/'draft/visual-plan.md'; plan.write_text('已有截图清楚，保留；无需新增。')
            artifacts=required_artifacts(project,{'blog'})
            self.assertIn('draft/visual-plan.md',artifacts)
            report={'status':'passed','voice_mode':'cold-start','voice_limitation':'没有历史样本','artifacts':{n:digest(project/n) for n in artifacts},'reviews':{'polished':{k:'只处理给定自述，已逐句检查' for k in ('voice','naturalness','typos','format','facts')}},'fact_checks':[],'fact_scope':'作者自述'}
            (project/'draft/editorial-review.json').write_text(json.dumps(report))
            self.assertEqual([],validate_editorial(project,{}, {'blog'}))
            plan.write_text('改为新增两张图，需要重新查看全文。')
            self.assertTrue(any('过期' in e for e in validate_editorial(project,{}, {'blog'})))
