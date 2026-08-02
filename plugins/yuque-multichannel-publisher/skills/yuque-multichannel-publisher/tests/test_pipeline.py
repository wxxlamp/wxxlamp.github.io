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
                "corpus_fingerprint": pipeline.VOICE_REFERENCE_FINGERPRINT,
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


if __name__ == "__main__":
    unittest.main()
