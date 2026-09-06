import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from reference_links import references, reference_context, resolve_reference, validate_reference_language, translation_reference_errors


class ReferenceLinksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'_config.yml').write_text('url: https://blog.example\npermalink: :year/:month/:day/:title/\n')
        self.posts = self.root/'source/_posts'; (self.posts/'en').mkdir(parents=True)
        self.header = '---\ntitle: Test\ndate: 2025-01-02\ntags: [Java]\ncategories: [技术]\n'
        (self.posts/'test.md').write_text(self.header+'---\n正文')
        (self.posts/'en/test.md').write_text(self.header+'lang: en\ntranslation_of: test\n---\nEnglish')
        catalog = self.root/'source/_data/references.json'; catalog.parent.mkdir()
        catalog.write_text(json.dumps({'site_aliases':['old.example'], 'route_aliases':{'/2025/01/02/旧标题/':'/2025/01/02/test/'}, 'pairs':[{'zh':'https://docs.example/zh/topic','en':'https://docs.example/en/topic'}]}))
        self.context = reference_context(self.root)

    def test_markdown_html_bare_urls_and_code_exclusion(self):
        text = '[A][a]\n\n[a]: /2025/01/02/test/\n\n<a href="/2025/01/02/test/#锚点">B</a>\n\nhttps://old.example/2025/01/02/test/\n\n![image](https://img.example/x.png)\n\n`https://code.example`\n\n```\nhttps://code.example/fenced\n```'
        refs = references(text)
        self.assertEqual(3, len(refs))
        self.assertFalse(any('code.example' in u or 'img.example' in u for u, _ in refs))

    def test_bidirectional_links_keep_query_fragment_and_alias(self):
        url = 'https://old.example/2025/01/02/%E6%97%A7%E6%A0%87%E9%A2%98/?a=1#section'
        english, state = resolve_reference(url, 'en', self.context)
        self.assertEqual('matched', state)
        self.assertEqual('https://old.example/en/2025/01/02/test/?a=1#section', english)
        self.assertEqual('/2025/01/02/test/#section', resolve_reference('/en/2025/01/02/test/#section','zh',self.context)[0])
        self.assertTrue(validate_reference_language('[Wrong](/2025/01/02/test/)', 'en', self.context))
        self.assertEqual([], validate_reference_language('[Right](/en/2025/01/02/test/)', 'en', self.context))

    def test_no_fabricated_english_route_and_explicit_original_label(self):
        (self.posts/'en/test.md').unlink(); ctx=reference_context(self.root)
        self.assertEqual('unavailable', resolve_reference('/2025/01/02/test/','en',ctx)[1])
        self.assertTrue(validate_reference_language('[Source](/2025/01/02/test/)', 'en',ctx))
        self.assertEqual([],validate_reference_language('[Source (in Chinese)](/2025/01/02/test/)', 'en',ctx))
        self.assertTrue(validate_reference_language('[Invented](/en/2025/01/02/test/)', 'en',ctx))

    def test_preservation_accepts_real_translation_but_not_dropped_reference(self):
        source='[Internal](/2025/01/02/test/) [Docs](https://docs.example/zh/topic)'
        target='[Internal](/en/2025/01/02/test/) [Docs](https://docs.example/en/topic)'
        self.assertEqual([],translation_reference_errors(source,target,self.context,{}))
        self.assertTrue(translation_reference_errors(source,'[Internal](/en/2025/01/02/test/)',self.context,{}))
        self.assertTrue(translation_reference_errors(source,source,self.context,{}))

    def test_external_alternatives_require_real_review_and_cannot_override_internal(self):
        plan={'reference_links':[{'source_url':'https://other.example/cn','url':'https://other.example/en','review_status':'passed','review_note':'Read both official pages; same material and section.'}]}
        self.assertEqual([],translation_reference_errors('[A](https://other.example/cn)','[A](https://other.example/en)',self.context,plan))
        plan['reference_links'][0]['review_status']='pending'
        self.assertTrue(translation_reference_errors('[A](https://other.example/cn)','[A](https://other.example/en)',self.context,plan))
        plan['reference_links'][0].update(source_url='/2025/01/02/test/',review_status='passed')
        self.assertTrue(translation_reference_errors('[A](/2025/01/02/test/)','[A](https://other.example/en)',self.context,plan))

    def test_empty_citation_is_rejected(self):
        self.assertTrue(validate_reference_language('[Missing source]()', 'en', self.context))

    def test_original_external_source_needs_language_label(self):
        self.context['original_sources']=[{'url':'https://original.example/article','language':'zh'}]
        self.assertTrue(validate_reference_language('[Source](https://original.example/article)','en',self.context))
        self.assertEqual([],validate_reference_language('[Source (in Chinese)](https://original.example/article)','en',self.context))
        self.assertEqual([],validate_reference_language('[原文](https://original.example/article)','zh',self.context))

    def test_materializing_current_article_does_not_stale_other_references(self):
        before=reference_context(self.root,'new')['sha256']
        (self.posts/'new.md').write_text(self.header+'---\nNew')
        self.assertEqual(before,reference_context(self.root,'new')['sha256'])
        (self.posts/'en/test.md').unlink()
        self.assertNotEqual(before,reference_context(self.root,'new')['sha256'])

if __name__ == '__main__': unittest.main()
