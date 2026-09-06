import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import pipeline  # noqa: E402


class PipelineContractTest(unittest.TestCase):
    @staticmethod
    def section_image(url: str = "https://example.com/section.png") -> dict:
        return {
            "url": url,
            "ratio": "16:9",
            "section_claim": "解释本节的具体关系",
            "visual_type": "process-diagram",
            "must_show": ["输入", "输出"],
            "avoid": ["无关装饰"],
            "prompt": "画出输入到输出的清晰流程",
            "review_status": "passed",
        }

    @staticmethod
    def wechat_cover() -> dict:
        return {
            "url": "https://example.com/wechat.png",
            "ratio": "2.35:1",
            "title": "我把内容分发做成插件",
            "title_safe_area": "left-center",
            "review_status": "passed",
        }

    def test_ratio_and_heading_contract(self) -> None:
        self.assertAlmostEqual(pipeline.ratio_value("21:9"), 21 / 9)
        self.assertAlmostEqual(pipeline.ratio_value("23:9"), 23 / 9)
        self.assertAlmostEqual(pipeline.ratio_value("2.35:1"), 2.35)
        self.assertTrue(pipeline.heading_numbered(1, "1. 前言"))
        self.assertTrue(pipeline.heading_numbered(2, "3.1. 下载语雀"))
        self.assertFalse(pipeline.heading_numbered(2, "下载语雀"))

    def test_blog_only_draft_does_not_require_other_channels(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            polished = project / "draft" / "polished.md"
            polished.parent.mkdir(parents=True)
            polished.write_text(
                "![封面](https://example.com/cover.png)\n\n"
                "# 1. 前言\n\n"
                "![章节图](https://example.com/section.png)\n\n正文。\n",
                encoding="utf-8",
            )
            metadata = {
                "title": "测试",
                "description": "用于验证按需选择渠道时，只校验已选择平台的测试描述。",
                "channels": ["blog"],
                "cover_ratio": "21:9",
                "lead_image_style": "ghibli-inspired",
                "cover_image": {"url": "https://example.com/cover.png", "ratio": "21:9", "style": "ghibli-inspired"},
                "section_images": {"1. 前言": self.section_image()},
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertEqual([], errors)

    def test_unnumbered_heading_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            polished = project / "draft" / "polished.md"
            polished.parent.mkdir(parents=True)
            polished.write_text(
                "![封面](https://example.com/cover.png)\n\n"
                "# 前言\n\n"
                "![章节图](https://example.com/section.png)\n",
                encoding="utf-8",
            )
            metadata = {
                "title": "测试",
                "description": "用于验证标题编号约束的测试描述。",
                "channels": ["blog"],
                "cover_ratio": "21:9",
                "lead_image_style": "ghibli-inspired",
                "cover_image": {"url": "https://example.com/cover.png", "ratio": "21:9", "style": "ghibli-inspired"},
                "section_images": {"前言": self.section_image()},
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertTrue(any("缺少 1 级数字序号" in error for error in errors))

    def test_wechat_requires_dedicated_235_cover(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            draft = project / "draft"
            draft.mkdir(parents=True)
            (draft / "polished.md").write_text(
                "![首图](https://example.com/lead.png)\n\n"
                "# 1. 前言\n\n![章节图](https://example.com/section.png)\n",
                encoding="utf-8",
            )
            (draft / "wechat.md").write_text("公众号正文。\n", encoding="utf-8")
            (draft / "wechat.html").write_text('<p style="color:#222">公众号正文。</p>\n', encoding="utf-8")
            metadata = {
                "title": "测试",
                "description": "用于验证微信公众号必须使用独立封面的测试描述。",
                "channels": ["wechat"],
                "cover_ratio": "21:9",
                "lead_image_style": "ghibli-inspired",
                "cover_image": {
                    "url": "https://example.com/lead.png",
                    "ratio": "21:9",
                    "style": "ghibli-inspired",
                },
                "section_images": {
                    "1. 前言": self.section_image()
                },
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertIn("metadata.json 缺少微信公众号公开 HTTPS 封面地址", errors)
            self.assertIn("微信公众号封面比例必须为 2.35:1", errors)

    def test_wechat_cover_requires_checked_title(self) -> None:
        cover = self.wechat_cover()
        self.assertEqual("passed", cover["review_status"])
        self.assertTrue(8 <= len(cover["title"]) <= 14)

    def test_wechat_large_rewrite_is_rejected(self) -> None:
        blog = "# 1. 原理\n\n这是一篇保留完整论证、例子和实现细节的博客正文。\n"
        wechat = "这是一段完全不同的公众号摘要。\n"
        self.assertLess(pipeline.content_similarity(blog, wechat), 0.9)
        self.assertEqual(1.0, pipeline.content_similarity(blog, blog))

    def test_polish_expand_requires_complete_ai_tone_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            polished = project / "draft" / "polished.md"
            polished.parent.mkdir(parents=True)
            polished.write_text(
                "![封面](https://example.com/cover.png)\n\n"
                "# 1. 前言\n\n![章节图](https://example.com/section.png)\n\n正文。\n",
                encoding="utf-8",
            )
            metadata = {
                "title": "测试",
                "description": "验证补充润色必须经过 AI 去味复审。",
                "edit_mode": "polish-expand",
                "channels": ["blog"],
                "cover_ratio": "21:9",
                "lead_image_style": "ghibli-inspired",
                "cover_image": {"url": "https://example.com/cover.png", "ratio": "21:9", "style": "ghibli-inspired"},
                "section_images": {"1. 前言": self.section_image()},
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertTrue(any("去 AI 味复审" in error for error in errors))
            metadata["ai_tone_review"] = {
                "status": "passed",
                "checks": sorted(pipeline.AI_TONE_CHECKS),
                "corpus_fingerprint": "a" * 64,
                "voice_reference": ".codex/yuque-multichannel-publisher/style-profiles/author-voice.md",
                "notes": "AI 已结合语气档案复审。",
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertEqual([], errors)

    def test_ai_tone_phrase_scan_only_reports_risks(self) -> None:
        risks = pipeline.ai_tone_risks("随着技术不断发展，值得注意的是，这套方案可以赋能团队。")
        self.assertIn("模板化时代开场", risks)
        self.assertIn("机械提示语", risks)
        self.assertIn("空泛商业黑话", risks)
        self.assertIn("否定对照句", pipeline.ai_tone_risks("这不是排版工具，而是内容流水线。"))

    def test_rednote_accepts_ai_planned_two_round_series(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            project = root / "content-projects" / "demo"
            rednote = project / "draft" / "rednote"
            rednote.mkdir(parents=True)
            polished = project / "draft" / "polished.md"
            polished.write_text(
                "![封面](https://example.com/cover.png)\n\n"
                "# 1. 前言\n\n![章节图](https://example.com/section.png)\n\n正文。\n",
                encoding="utf-8",
            )
            for round_name in ("round1", "round2"):
                path = rednote / round_name / "post.md"
                path.parent.mkdir()
                path.write_text(
                    "# 标题\n\n"
                    "![1](https://example.com/1.png)\n"
                    "![2](https://example.com/2.png)\n"
                    "![3](https://example.com/3.png)\n\n正文。\n\n#标签一 #标签二 #标签三 #标签四 #标签五\n",
                    encoding="utf-8",
                )
                (path.parent / "cards.json").write_text(
                    json.dumps(
                        {
                            "cards": [
                                {
                                    "index": index,
                                    "role": "cover" if index == 1 else "content",
                                    "headline": f"卡片{index}",
                                    "body": "独立说明本轮主题。",
                                    "visual_strategy": "pure_text",
                                    "material_ref": "测试材料",
                                }
                                for index in range(1, 4)
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
            (rednote / "series-plan.json").write_text(
                json.dumps(
                    {
                        "round_count_reason": "文章只有原因和做法两个独立主题，因此规划两轮。",
                        "rounds": [
                            {
                                "round": "round1",
                                "angle": "原因",
                                "subject": "内容插件",
                                "target_reader": "多平台作者",
                                "core_viewpoint": "重复分发值得自动化",
                                "context_brief": "说明语雀文章需要分发到多个平台",
                                "reader_promise": "理解原因",
                                "hook": "为什么要做？",
                                "image_plan": ["封面", "原因", "结论"],
                            },
                            {
                                "round": "round2",
                                "angle": "做法",
                                "subject": "内容插件",
                                "target_reader": "多平台作者",
                                "core_viewpoint": "AI 与脚本需要分工",
                                "context_brief": "说明插件加工一篇语雀文章",
                                "reader_promise": "学会做法",
                                "hook": "应该怎么做？",
                                "image_plan": ["封面", "步骤", "结论"],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            metadata = {
                "title": "测试",
                "description": "用于验证小红书轮数由 AI 根据内容规划的测试描述。",
                "channels": ["rednote"],
                "cover_ratio": "21:9",
                "lead_image_style": "ghibli-inspired",
                "cover_image": {"url": "https://example.com/cover.png", "ratio": "21:9", "style": "ghibli-inspired"},
                "section_images": {"1. 前言": self.section_image()},
            }
            errors, _ = pipeline.validate_draft(project, metadata)
            self.assertEqual([], errors)

    def test_materialize_writes_final_channel_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            project = root / "content-projects" / "demo"
            (project / ".codex").mkdir(parents=True)
            (project / "draft" / "rednote").mkdir(parents=True)
            metadata = {
                "project": "demo",
                "title": "测试文章",
                "description": "验证物化目录。",
                "channels": ["blog", "wechat", "rednote"],
                "tags": ["测试"],
                "categories": ["测试"],
            }
            (project / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            (project / ".codex" / "state.json").write_text(
                json.dumps({"current_stage": "reviewed", "checkpoints": []}), encoding="utf-8"
            )
            (project / "draft" / "polished.md").write_text("博客正文。\n", encoding="utf-8")
            (project / "draft" / "wechat.md").write_text("博客正文。\n", encoding="utf-8")
            (project / "draft" / "wechat.html").write_text('<p style="color:#222">博客正文。</p>\n', encoding="utf-8")
            (project / "draft" / "rednote" / "series-plan.json").write_text(
                json.dumps({"rounds": []}), encoding="utf-8"
            )
            for number in range(1, 4):
                post = project / "draft" / "rednote" / f"round{number}" / "post.md"
                post.parent.mkdir()
                post.write_text(f"# 第{number}轮\n", encoding="utf-8")
                (post.parent / "cards.json").write_text(json.dumps({"cards": []}), encoding="utf-8")
            with patch.dict(os.environ, {"YMP_WORKSPACE_ROOT": str(root)}):
                pipeline.command_materialize(SimpleNamespace(project="demo", allow_incomplete=True))
            self.assertTrue((root / "source" / "_posts" / "demo.md").is_file())
            self.assertTrue((root / "wechat" / "demo" / "article.md").is_file())
            self.assertTrue((root / "wechat" / "demo" / "article.html").is_file())
            self.assertTrue((root / "rednote" / "demo" / "series-plan.json").is_file())
            for number in range(1, 4):
                self.assertTrue((root / "rednote" / "demo" / f"round{number}" / "post.md").is_file())
                self.assertTrue((root / "rednote" / "demo" / f"round{number}" / "cards.json").is_file())

    def test_delivery_state_is_independent_per_platform_and_round(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / ".codex").mkdir()
            state = {"current_stage": "persisted", "deliveries": {}}
            wechat = pipeline.record_delivery(
                project,
                state,
                channel="wechat",
                item="article",
                status="draft_saved",
                account="official-account",
            )
            rednote = pipeline.record_delivery(
                project,
                state,
                channel="rednote",
                item="round1",
                status="filled_for_review",
            )
            saved = json.loads((project / ".codex" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual("draft_saved", wechat["status"])
            self.assertEqual("filled_for_review", rednote["status"])
            self.assertEqual("draft_saved", saved["deliveries"]["wechat"]["article"]["status"])
            self.assertEqual("filled_for_review", saved["deliveries"]["rednote"]["round1"]["status"])
            self.assertEqual("persisted", saved["current_stage"])

    def test_adapter_errors_redact_secret_and_explain_ip_whitelist(self) -> None:
        raw = (
            'Get "https://api.weixin.qq.com/cgi-bin/token?appid=wx123&secret=top-secret": '
            "errcode=40164, invalid ip 203.0.113.8, not in whitelist"
        )
        redacted = pipeline.redact_adapter_secrets(raw)
        self.assertNotIn("top-secret", redacted)
        nested = pipeline.redact_adapter_payload({"error": raw})
        self.assertNotIn("top-secret", nested["error"])
        message = pipeline.adapter_error_message({"message": raw})
        self.assertIn("203.0.113.8", message)
        self.assertIn("IP 白名单", message)

    def test_wechat_probe_allows_existing_html_when_only_format_api_is_missing(self) -> None:
        target = {"ready": True, "blockers": [], "warnings": []}
        pipeline.apply_wechat_probe(
            target,
            {
                "success": True,
                "data": {"overall": "blocked", "readiness": {"format_api": False, "draft": True}},
            },
            0,
        )
        self.assertTrue(target["ready"])
        self.assertTrue(target["draft_api_ready"])
        self.assertFalse(target["format_api_ready"])
        self.assertTrue(any("article.html" in warning for warning in target["warnings"]))

    def test_wechat_send_draft_reuses_html_and_records_media_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            project = root / "content-projects" / "demo"
            (project / ".codex").mkdir(parents=True)
            images = project / "images"
            images.mkdir()
            cover = images / "wechat-cover.png"
            body_image = images / "section.png"
            cover.write_bytes(b"cover")
            body_image.write_bytes(b"body")
            source_url = "https://cdn.example.com/section.png"
            metadata = {
                "project": "demo",
                "title": "测试公众号草稿",
                "description": "验证直接复用现成 HTML 保存公众号草稿。",
                "channels": ["wechat"],
                "wechat_cover_image": {"local": str(cover), "url": "https://cdn.example.com/cover.png"},
                "section_images": {"1. 测试": {"local": str(body_image), "url": source_url}},
            }
            (project / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
            (project / ".codex" / "state.json").write_text(
                json.dumps({"current_stage": "persisted", "deliveries": {}}), encoding="utf-8"
            )
            final = root / "wechat" / "demo"
            final.mkdir(parents=True)
            (final / "article.md").write_text("公众号正文。\n", encoding="utf-8")
            (final / "article.html").write_text(
                f'<section><img src="{source_url}"><p>公众号正文。</p></section>\n', encoding="utf-8"
            )
            adapter = root / "bin" / "md2wechat"
            adapter.parent.mkdir()
            adapter.write_text("adapter", encoding="utf-8")
            config_dir = root / ".codex" / "yuque-multichannel-publisher"
            config_dir.mkdir(parents=True)
            (config_dir / "config.json").write_text(
                json.dumps({"md2wechat_executable": str(adapter)}), encoding="utf-8"
            )
            captured_draft: dict = {}

            def fake_adapter(command: list[str], *, cwd: Path, timeout: int = 180):
                action = command[1]
                if action == "doctor":
                    return {"success": True, "data": {"readiness": {"draft": True, "format_api": False}}}
                if action == "inspect":
                    return {"success": True, "data": {"ready": True}}
                if action == "upload_image":
                    is_cover = command[2].endswith("wechat-cover.png")
                    return {
                        "success": True,
                        "data": {
                            "media_id": "cover-media" if is_cover else "body-media",
                            "wechat_url": (
                                "http://mmbiz.qpic.cn/cover.png" if is_cover else "http://mmbiz.qpic.cn/body.png"
                            ),
                        },
                    }
                if action == "create_draft":
                    captured_draft.update(json.loads(Path(command[2]).read_text(encoding="utf-8")))
                    return {"success": True, "data": {"media_id": "draft-media-id"}}
                self.fail(f"unexpected adapter action: {action}")

            with patch.dict(os.environ, {"YMP_WORKSPACE_ROOT": str(root)}), patch.object(
                pipeline, "run_adapter_json", side_effect=fake_adapter
            ):
                pipeline.command_send_draft(
                    SimpleNamespace(project="demo", channel="wechat", round=None, account=None, confirm=True)
                )
            article = captured_draft["articles"][0]
            self.assertEqual("cover-media", article["thumb_media_id"])
            self.assertIn("http://mmbiz.qpic.cn/body.png", article["content"])
            self.assertNotIn(source_url, article["content"])
            saved = json.loads((project / ".codex" / "state.json").read_text(encoding="utf-8"))
            delivery = saved["deliveries"]["wechat"]["article"]
            self.assertEqual("draft_saved", delivery["status"])
            self.assertEqual("draft-media-id", delivery["identifier"])

    def test_resume_actions_do_not_collapse_channel_delivery_state(self) -> None:
        metadata = {"channels": ["blog", "wechat", "rednote"]}
        state = {
            "current_stage": "persisted",
            "deliveries": {
                "wechat": {"article": {"status": "draft_saved"}},
                "rednote": {"round1": {"status": "filled_for_review"}},
            },
        }
        actions = {item["target"]: item["action"] for item in pipeline.delivery_next_actions(metadata, state)}
        self.assertEqual("review-repository-diff", actions["blog"])
        self.assertEqual("review-platform-draft", actions["wechat"])
        self.assertEqual("save-platform-draft-manually", actions["rednote"])

    def test_rednote_parser_keeps_images_and_removes_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            post = Path(temp) / "post.md"
            post.write_text(
                "# 二十字以内标题\n\n正文。\n\n![卡片](https://example.com/card.png)\n\n#标签一 #标签二\n",
                encoding="utf-8",
            )
            title, body, images = pipeline.markdown_title_and_body(post)
            self.assertEqual("二十字以内标题", title)
            self.assertNotIn("# 二十字以内标题", body)
            self.assertEqual(["https://example.com/card.png"], images)

    def test_rednote_adapter_is_preview_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            project = root / "content-projects" / "demo"
            (project / ".codex").mkdir(parents=True)
            (project / "draft").mkdir()
            (project / "metadata.json").write_text(
                json.dumps({"project": "demo", "channels": ["rednote"]}), encoding="utf-8"
            )
            (project / ".codex" / "state.json").write_text(
                json.dumps({"current_stage": "persisted", "deliveries": {}}), encoding="utf-8"
            )
            final_round = root / "rednote" / "demo" / "round1"
            final_round.mkdir(parents=True)
            (final_round / "post.md").write_text(
                "# 标题\n\n正文。\n\n![图](https://example.com/1.png)\n", encoding="utf-8"
            )
            (final_round / "cards.json").write_text(json.dumps({"cards": []}), encoding="utf-8")
            (final_round.parent / "series-plan.json").write_text(json.dumps({"rounds": []}), encoding="utf-8")
            adapter = root / "xhs" / "scripts" / "publish_pipeline.py"
            adapter.parent.mkdir(parents=True)
            adapter.write_text("# adapter\n", encoding="utf-8")
            config_dir = root / ".codex" / "yuque-multichannel-publisher"
            config_dir.mkdir(parents=True)
            (config_dir / "config.json").write_text(
                json.dumps({
                    "xiaohongshu_skills_dir": str(adapter.parents[1]),
                    "rednote_allow_browser_launch": True,
                }),
                encoding="utf-8",
            )
            captured: list[list[str]] = []

            def fake_run(command: list[str], *, cwd: Path):
                captured.append(command)
                return SimpleNamespace(returncode=0)

            with patch.dict(os.environ, {"YMP_WORKSPACE_ROOT": str(root)}), patch.object(
                pipeline, "run_checked", side_effect=fake_run
            ):
                pipeline.command_send_draft(
                    SimpleNamespace(project="demo", channel="rednote", round="round1", account=None, confirm=True)
                )
            self.assertEqual(1, len(captured))
            self.assertIn("--preview", captured[0])
            self.assertIn("--reuse-existing-tab", captured[0])
            self.assertNotIn("--headless", captured[0])


if __name__ == "__main__":
    unittest.main()
