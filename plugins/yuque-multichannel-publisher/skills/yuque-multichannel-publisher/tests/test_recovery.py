import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline
import yuque_fetcher
import image_uploader
from wechat_layout import render
from editorial_quality import validate_html_fidelity
from reference_links import reference_context, translation_reference_errors, resolve_reference


class RecoveryTests(unittest.TestCase):
    def test_default_edit_mode_does_not_expand_complete_article(self):
        args = pipeline.build_parser().parse_args(['init', '--project', 'demo', '--yuque-url', 'https://www.yuque.com/a/b/c'])
        self.assertEqual('correction-only', args.edit_mode)

    def test_pending_moderation_is_separate_from_publication(self):
        with tempfile.TemporaryDirectory() as d:
            state = {'current_stage': 'persisted'}
            pipeline.record_delivery(Path(d), state, channel='rednote', item='round1', status='submitted')
            self.assertEqual('submitted', json.loads((Path(d)/'.codex/state.json').read_text())['deliveries']['rednote']['round1']['status'])
            actions = pipeline.delivery_next_actions({'channels': ['rednote']}, state)
            self.assertEqual('check-moderation-result', actions[0]['action'])

    def test_existing_and_uncertain_drafts_cannot_be_blindly_recreated(self):
        saved = {'status':'draft_saved', 'artifact_sha256':'same', 'identifier':'media'}
        self.assertEqual('media', pipeline.existing_wechat_draft(saved, 'same'))
        with self.assertRaises(SystemExit): pipeline.existing_wechat_draft(saved, 'changed')
        self.assertIsNone(pipeline.existing_wechat_draft(saved, 'changed', True))
        for status in ('unknown', 'submitted'):
            with self.assertRaises(SystemExit): pipeline.existing_wechat_draft({'status':status}, 'same', True)
        with self.assertRaises(SystemExit): pipeline.existing_wechat_draft({'status':'draft_saved', 'identifier':'legacy'}, 'same')

    def test_effective_config_is_allowlisted_without_exposing_credentials(self):
        payload = {'data':{'config':{'wechat_appid':'wx123456789', 'wechat_secret':'sensitive', 'image_api_key':'sensitive', 'wechat_proxy_url':'https://user:pass@proxy.example', 'config_file':'/tmp/config'}}}
        with patch.object(pipeline, 'run_adapter_json', return_value=payload) as adapter, patch.dict(os.environ, {'HTTPS_PROXY':'https://user:pass@proxy.example'}):
            summary = pipeline.wechat_config_summary('adapter', Path('/tmp'))
        text = json.dumps(summary)
        self.assertNotIn('sensitive', text)
        self.assertNotIn('user:pass', text)
        self.assertEqual('456789', summary['default_appid_suffix'])
        self.assertFalse(summary['api_authentication_verified'])
        self.assertNotIn('--show-secret', adapter.call_args.args[0])
        redacted = pipeline.redact_adapter_payload({'data':{'wechat_secret':'sensitive', 'access_token':'sensitive'}})
        self.assertNotIn('sensitive', json.dumps(redacted))

    def test_material_cache_is_account_scoped_and_legacy_not_reused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); local = root/'crop.png'; local.write_bytes(b'cropped')
            pipeline.atomic_json(root/'.codex/wechat-materials.json', {'items':{'file:'+pipeline.file_digest(local):{'media_id':'wrong-account', 'wechat_url':'https://old'}}})
            responses = [{'data':{'media_id':a, 'wechat_url':'https://img/'+a}} for a in ('one','two')]
            with patch.object(pipeline, 'run_adapter_json', side_effect=responses) as call:
                first = pipeline.upload_wechat_material('adapter', repo=root, project=root, account='one', source='crop', local_path=local)
                again = pipeline.upload_wechat_material('adapter', repo=root, project=root, account='one', source='crop', local_path=local)
                other = pipeline.upload_wechat_material('adapter', repo=root, project=root, account='two', source='crop', local_path=local)
            self.assertEqual(first, again)
            self.assertNotEqual(first, other)
            self.assertEqual(2, call.call_count)

    def test_reviewed_crop_is_uploaded_instead_of_original_and_stale_crop_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root/'raw').mkdir(); (root/'images').mkdir()
            display = root/'images/crop.png'; display.write_bytes(b'only-visible-region')
            url = 'https://cdn.example/img.png?x=1&y=2'
            manifest = root/'raw/image-display.json'
            manifest.write_text(json.dumps({'images':[{'source_url':url, 'display':'images/crop.png', 'display_sha256':pipeline.file_digest(display), 'review_status':'passed', 'review_note':'Matches visible crop'}]}))
            md = '<img src="https://cdn.example/img.png?x=1&amp;y=2">'
            session = Mock(); session.cookies.return_value = {}
            with patch.object(yuque_fetcher, 'download_image') as download, patch.object(yuque_fetcher, 'upload_file', return_value={'url':'https://host/crop.png'}) as upload:
                result = yuque_fetcher.migrate_images(md, session=session, root=root, provider='github', image_manifest=manifest)
                download.assert_not_called()
                self.assertEqual(display, upload.call_args.args[0])
                self.assertEqual('<img src="https://host/crop.png">', result)
                display.write_bytes(b'changed')
                with self.assertRaises(ValueError):
                    yuque_fetcher.migrate_images(md, session=session, root=root, provider='github', image_manifest=manifest)
                self.assertEqual(1, upload.call_count)

    def test_custom_timeline_and_prominent_headings_keep_words_numbers_and_links(self):
        md = '# 1. 经历\n\n<section style="border-left:3px solid #abc"><p><strong>2023</strong>原句；</p><p>2026：<strong>95%</strong>。</p></section>\n\n![图](https://img.example/one.png)\n\n[出处](https://example.com/docs)'
        result = render(md, article_type='essay', image_frame='shadow', heading_style='prominent', preserve_html=True)
        self.assertEqual([], validate_html_fidelity(md, result))
        self.assertIn('<section style="border-left:3px solid #abc">', result)
        self.assertIn('font-size:24px', result)
        self.assertIn('box-shadow:0 2px 8px', result)
        with self.assertRaises(ValueError): render(md)

    def test_homepage_translation_uses_reviewed_page_routes_without_duplicate_source_link(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root/'source/_data').mkdir(parents=True)
            (root/'_config.yml').write_text('url: https://blog.example\n')
            catalog = root/'source/_data/references.json'
            catalog.write_text(json.dumps({'page_pairs':[{'zh':'/', 'en':'/en/'}, {'zh':'/about/', 'en':'/en/about/'}]}))
            context = reference_context(root)
            self.assertEqual(('https://blog.example/en/?x=1#bio','matched'), resolve_reference('https://blog.example/?x=1#bio','en',context))
            self.assertEqual([], translation_reference_errors('[首页](https://blog.example/)','[Home](https://blog.example/en/)',context,{}))
            self.assertEqual('local', resolve_reference('/unknown/', 'en', context)[1])

    @staticmethod
    def response(code, payload):
        response = Mock(status_code=code)
        response.json.return_value = payload
        return response

    def test_github_retry_reuses_identical_blob_and_pins_commit(self):
        with tempfile.TemporaryDirectory() as d:
            local = Path(d)/'crop.png'; local.write_bytes(b'crop')
            blob = hashlib.sha1(b'blob 4\0crop').hexdigest()
            with patch.object(image_uploader.requests, 'get', side_effect=[self.response(200, {'sha':'a'*40}), self.response(200, {'sha':blob})]), patch.object(image_uploader.requests, 'put') as put:
                result = image_uploader.upload_github(local, {'github_owner':'owner', 'github_repo':'repo'}, 'test-token')
            put.assert_not_called()
            self.assertTrue(result['reused'])
            self.assertIn('@'+'a'*40+'/', result['url'])
            self.assertEqual(hashlib.sha256(b'crop').hexdigest(), result['sha256'])

    def test_github_new_file_uses_returned_commit_and_collision_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            local = Path(d)/'crop.png'; local.write_bytes(b'crop')
            with patch.object(image_uploader.requests, 'get', side_effect=[self.response(200, {'sha':'a'*40}), self.response(404, {})]), patch.object(image_uploader.requests, 'put', return_value=self.response(201, {'commit':{'sha':'b'*40}})) as put:
                result = image_uploader.upload_github(local, {'github_owner':'owner', 'github_repo':'repo'}, 'test-token')
            self.assertFalse(result['reused'])
            self.assertIn('@'+'b'*40+'/', result['url'])
            self.assertNotIn('sha', put.call_args.kwargs['json'])
            with patch.object(image_uploader.requests, 'get', side_effect=[self.response(200, {'sha':'a'*40}), self.response(200, {'sha':'different'})]), patch.object(image_uploader.requests, 'put') as put:
                with self.assertRaises(RuntimeError): image_uploader.upload_github(local, {'github_owner':'owner', 'github_repo':'repo'}, 'test-token')
                put.assert_not_called()

    def test_priority_materialization_preserves_other_outputs_and_delivery(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'YMP_WORKSPACE_ROOT':d}):
            root=Path(d); project=root/'content-projects/demo'; (project/'draft').mkdir(parents=True)
            for name, body in [('polished.md','原文'), ('wechat.md','原文'), ('wechat.html','<p>原文</p>')]: (project/'draft'/name).write_text(body)
            state={'current_stage':'reviewed', 'outputs':{'blog':{'path':'existing'}}, 'deliveries':{'rednote':{'round1':{'status':'submitted'}}}}
            pipeline.atomic_json(project/'.codex/state.json', state)
            pipeline.atomic_json(project/'metadata.json', {'project':'demo','channels':['blog','wechat','rednote'],'title':'标题'})
            with patch.object(pipeline, 'validate_draft', return_value=([],[])) as check:
                pipeline.command_materialize(SimpleNamespace(project='demo', channels=['wechat'], allow_incomplete=False))
            self.assertEqual(['wechat'], check.call_args.args[1]['channels'])
            self.assertTrue((root/'wechat/demo/article.html').is_file())
            saved=json.loads((project/'.codex/state.json').read_text())
            self.assertEqual({'path':'existing'}, saved['outputs']['blog'])
            self.assertEqual(state['deliveries'], saved['deliveries'])
            self.assertFalse((root/'source/_posts/demo.md').exists())


if __name__ == '__main__': unittest.main()
