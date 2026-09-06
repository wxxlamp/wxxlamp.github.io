---
title: Building a Codex Plugin for Multichannel Publishing from Yuque
tags:
  - AI 编程
  - 研发效能
  - 博客与写作
categories:
  - 场景实践
description: >-
  I bundled polishing Yuque long-form articles, image creation, three-platform
  adaptation, quality checks, and draft delivery into a Codex Plugin, while
  documenting the real limits of platform automation.
lang: en
translation_of: yuque-multichannel-publisher
date: 2026-08-02 17:28:50
---
![A long article passes through a resumable workflow to become publication packages for three channels](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b2c5bb2c_cover.png)

I usually finish writing an article in Yuque first.

But after the final sentence, the work is not over: a blog, WeChat Official Account, and RedNote each have their own content format. I still need to reformat, illustrate, split, and check it, which takes roughly another two hours.

Recently, I made this workflow into a [Codex Plugin](https://github.com/wxxlamp/ai-coding-config/tree/main/plugins/yuque-multichannel-publisher). It reads the Yuque original, lets AI polish it, create images, and adapt it for platforms, then uses scripts for uploading, validation, persistence, resume support, and pre-publication checks. This article is its first complete test. I want to record how it was made and clarify what can truly be automated and what still needs a person to confirm on each platform page.

# 1. Why make content distribution a plugin?

![The repetitive flow from one Yuque long-form article to a blog, WeChat Official Account, and RedNote](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/69c25415_section-1.png)

I have always kept a blog, and usually put everyday writing in Yuque first. Once an article is finished, I publish it on my website, then prepare WeChat Official Account and RedNote versions. All three backends appear to accept pasted Markdown, but in practice each brings a pile of work.

A blog needs complete structure, code blocks, and Hexo front matter. A WeChat article cares more about mobile reading and needs a separate 2.35:1 cover. RedNote needs the long article reorganized into a short note and a set of vertical cards. Images cannot simply be reused either: a lead image, section image, WeChat cover, and RedNote card each have different jobs.

At first I gradually wrote several Skills under `.agents/skills/` in the repository: fetching Yuque, migrating images, uploading them to image hosting, and polishing Markdown. Each worked alone, but managing them together became increasingly difficult.

For example, the Yuque Skill knew only how to download an article locally, not where it should ultimately go. The polishing Skill could learn a voice, but did not know how much blog content WeChat should retain. The image-upload Skill certainly could not tell whether an image truly explained a section. Each run forced AI to reassemble those capabilities, and directories, parameters, and context were easily omitted. Copying the repository to someone else could also leave out an `.agents/skills` dependency.

The chain is long too. Yuque reading, polishing, image generation, upload, three-platform adaptation, and publishing can all be interrupted by a network or page problem. If progress exists only in the current session, the next run must reconstruct everything.

These issues convinced me that the whole workflow needed one Plugin. It should carry its own instructions, scripts, references, tests, and artifact contract, while keeping personal credentials and task progress in the workspace. Copying the plugin then does not copy tokens, and resuming a task does not require guessing where it stopped.

# 2. How I built the plugin

![The plugin's five-stage flow: reading, AI processing, scripting, quality checks, and three-channel output](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f2fe3dfa_section-2.png)

The plugin and this article were built entirely with Codex. Here is the general approach.

## 2.1. First define the boundary between AI and scripts

Voice judgment, content additions, image concepts, and platform adaptation need context, so I gave them to AI. AI also performs the final review, checking factual boundaries, heading numbering, image semantics, and platform differences.

Downloading files, uploading images, checking image ratios, comparing WeChat and blog bodies, creating directories, and recording state all have definite results, so scripts handle them. Scripts judge only whether files exist, ratios are correct, and fields are complete; they never secretly rewrite an author's body text.

This boundary became the plugin's core: AI can create, but must leave inspectable artifacts; scripts remain stable without reducing creative work to string replacement.

## 2.2. Bring scattered Skills into one Plugin

The old Yuque fetcher, image uploader, and voice cache became internal plugin components. Only one main Skill remains public, describing the full workflow and quality requirements. AI no longer finds multiple Skills temporarily or depends on the target repository's `.agents/` directory.

Yuque reading prefers an already logged-in browser session. This handles private documents, non-member pages, and API-policy changes. When Markdown can be copied from the page, formatting is retained directly; when it cannot, visible structure restores headings, lists, quotations, code, and images. Original images are reuploaded to the user's own image host.

## 2.3. Build an author-voice baseline from 86 earlier articles

I did not want each polish to reread historical articles, so AI first read the blog's 86 existing posts and compiled `author-voice.md`. This personal profile lives in `.codex/yuque-multichannel-publisher/style-profiles/` in the workspace and is not packaged into the Plugin.

After others install the plugin, their first run follows the same learning process, reading only historical posts in their own workspace. If no usable samples exist, the plugin explicitly uses a restrained general voice until enough articles exist to build a personal profile. The process creates only a voice reference, never keys. Image-host tokens must be supplied by environment variables or workspace configuration; WeChat and RedNote use the user's existing logged-in sessions.

The reference records a first-person engineer viewpoint, common openings, sentence and paragraph rhythm, technical reasoning patterns, ending habits, and expressions to avoid. Later polish reads only this compact baseline. If old posts change, update the corpus fingerprint; if a category genuinely differs, add a small category profile.

Voice protection has two passes. First preserve facts, adding only background, causality, examples, and boundaries needed to understand the article. Only then reorganize sentences and paragraphs according to the voice profile, retaining my first-person judgments, technical reasoning, hesitation, and natural transitions. This avoids inventing experiences merely to “sound like me.”

Then perform a de-AI review, targeting template openings, empty buzzwords, neat parallelism, universal summaries, and frequent negative-contrast phrasing. The project records the voice-profile path, corpus fingerprint, checks, and review notes. Scripts verify that evidence exists and scan high-risk language; AI still makes the final language judgment.

## 2.4. Give images content before style

The first section images had correct proportions and looked technological, but said little about their sections. I therefore split generation into three steps: write a visual brief, generate the image, and review it.

The brief states the section's core claim, required objects and relationships, appropriate information type, and elements to avoid. Processes and architecture prefer editorial infographics; real screenshots come first when material exists; personal experiences fit narrative illustration. Afterwards, inspect text, relationships, and thumbnail readability, redrawing if content does not match.

The body lead image retains a warm hand-drawn animation feel. Generate the WeChat cover separately at exactly 2.35:1 with a short title in the safe area. For RedNote, organize a card narrative first—each card advances one information point—then make 3:4 images.

## 2.5. Use checkpoints for long tasks

Every content project stores `state.json` and event records under `content-projects/<slug>/.codex/`. They contain the current stage, completed artifacts, hashes, and final target directory.

The plugin divides work into initialization, fetching, polishing, image creation, review, and persistence. After interruption, `resume` directly shows where it stopped. Only after the `reviewed` checkpoint is recorded may `materialize` write drafts into formal directories.

Finally, I added contract tests to the pipeline. They check heading numbering, image ratios and briefs, author-voice fingerprints, WeChat/blog body similarity, RedNote card counts, cross-round references, final directories, and whether platforms were mistakenly recorded with the same publishing status. After this test article ran, draft validation, materialization validation, and the Hexo build all passed.

# 3. Plugin structure, artifacts, and benefits

![A reviewed long article is persisted as publication packages for blog, WeChat, and RedNote](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/2000d4ab_section-3.png)

The plugin has one public Skill and roughly this directory structure:

```text
yuque-multichannel-publisher/
├── .codex-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── yuque-multichannel-publisher/
        ├── SKILL.md
        ├── assets/
        │   └── config.example.json
        ├── references/
        │   ├── voice-profile.md
        │   ├── editorial-guide.md
        │   ├── visual-direction.md
        │   ├── artifact-contract.md
        │   ├── style-profile-cache.md
        │   └── publishing.md
        ├── scripts/
        │   ├── pipeline.py
        │   ├── workspace.py
        │   ├── yuque_fetcher.py
        │   ├── image_uploader.py
        │   └── style_profiles.py
        └── tests/
            └── test_pipeline.py
```

`plugin.json` defines plugin identity, version, and Codex display information. `SKILL.md` tells AI how to complete the workflow. `references/` holds general standards for voice learning, editing, images, artifacts, and publishing. `scripts/` performs deterministic work, and `tests/` prevents directory and validation rules from silently breaking after updates.

Personal data lives separately in the workspace:

```text
<workspace>/.codex/yuque-multichannel-publisher/
├── config.json
├── browser-data/
└── style-profiles/
    ├── author-voice.md
    ├── profile-index.json
    └── style-*.json
```

At runtime, personal voice, login state, image-host tokens, category cache, and task state are not written to the plugin directory. They live in `.codex/yuque-multichannel-publisher/` in the workspace or in a concrete content project. The plugin only checks whether credentials are configured; it does not generate keys or read browser passwords. The plugin can be updated or copied without overwriting personal configuration.

## 3.1. How the three platforms are persisted

The blog retains full argument, code, citations, and table-of-contents structure, finally writing to:

```text
source/_posts/<slug>.md
```

WeChat uses the same body as the blog with only light paragraph adaptation, generating both Markdown and HTML with inline styles:

```text
wechat/<slug>/article.md
wechat/<slug>/article.html
```

RedNote first determines how many independent notes the original supports. Every round must reintroduce its subject and core claim, then generate its body and card plan:

```text
rednote/<slug>/series-plan.json
rednote/<slug>/round1/post.md
rednote/<slug>/round1/cards.json
```

This article ultimately creates only one round. Its motivation, production process, plugin structure, and benefits are one topic; splitting it into three rounds would leave the latter two without necessary context.

## 3.2. How RedNote decides the number of rounds

RedNote splitting considers themes first, then sections. AI extracts the article's subject, target reader, core judgment, actionable information, and real material, then judges whether each candidate theme remains complete when separated.

A round must answer three questions: what it discusses, why it is worth reading, and what readers can do. It also needs its own context, benefit, and visual material. A mere step in the long article, or content requiring “the previous round” to understand, remains in the same note.

After deciding the count, each round writes its context in `series-plan.json` before writing `cards.json`. The first card states the topic and target reader; each middle card advances one point; the last closes the conclusion or asks a concrete question. Images prioritize real screenshots and materials, then redraws, text-and-image cards, and AI scenes. Finally, read each round's body and cards separately as a “stranger-reader test.”

This article includes motivation, process, plugin structure, and benefits, but all answer “How was this plugin made?” Separating them would remove the structure and benefits from their product context, so one round remains.

## 3.3. Inspect first, then decide how to deliver drafts

Following [md2wechat](https://github.com/geekjourneyx/md2wechat-skill) and [XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills), I separated “generate publication packages” from “operate external platforms.” The pipeline first produces a machine-readable readiness report:

```bash
python3 pipeline.py inspect --project <slug> --probe
```

It lists body character count, heading count, remote images, summary length, AI-cliché risk, missing artifacts on all three channels, and adapter status. Subsequent actions trust only blockers in this report rather than guessing publishability from “the file was generated.”

WeChat can connect to a separately installed `md2wechat`. The plugin calls `inspect` to check account configuration, cover, and target status, then writes the draft. AppID, Secret, and API Key remain in the external tool's own configuration; the plugin saves only an executable path and account alias.

```bash
python3 pipeline.py send-draft \
  --project <slug> \
  --channel wechat \
  --confirm
```

RedNote is handled more conservatively. The reference project operates its creator backend through Chrome DevTools Protocol and can upload images and fill title and body, but automation is affected by page changes, login checks, and account risk control. The plugin therefore always calls its `--preview` mode: it fills only the editor, never clicks Publish, and never records “the page was filled” as “the platform draft was saved.”

```bash
python3 pipeline.py send-draft \
  --project <slug> \
  --channel rednote \
  --round round1 \
  --confirm
```

Only after RedNote explicitly reports a successful save does it record `draft_saved`. WeChat, RedNote, and every RedNote round each have their own status; `filled_for_review`, `draft_saved`, and `published` are also completely separate. Thus, a failed round does not roll back content stages already finished on other platforms.

Neither external project is packaged directly into the plugin. `md2wechat`'s license has extra requirements for commercial use and redistribution, while `XiaohongshuSkills` browser selectors must follow platform updates. Keeping an adapter layer means the plugin maintains only content contracts, capability probing, and state records; external tools can be installed and upgraded independently.

## 3.4. What I think is most valuable now

First, the plugin is self-contained: copying the directory carries the main Skill, internal scripts, references, and tests, without reassembling multiple repository Skills.

Second, AI's creative ability and scripts' stability have clear places. AI still creates articles, images, and channel adaptations, while scripts check directories, ratios, state, and similarity. When a problem appears, it is easier to know whether to change the prompt, reference, or code.

Third, long tasks are resumable. If image generation or browser automation stops, originals, drafts, images, and checkpoints remain locally and the next session can continue from the valid stage.

Fourth, the three channels share facts and a long-form draft but have independent artifact forms. WeChat does not become a summary, and RedNote is not mechanically split by first-level headings.

Fifth, quality requirements leave evidence. The project files show which voice reference was used, what a section image should express, whether the WeChat-cover title was checked, and why RedNote has its current number of rounds.

It still has boundaries. A WeChat draft box can be written through an external adapter, but credentials, IP allowlists, and account permissions still require user configuration. RedNote automation can reliably fill the editor, but whether a draft was actually saved must be confirmed from platform feedback. The blog repository also has its own Git rules. Before real publication, account, title, time, and visibility still need confirmation.

Plugin source and instructions are in [wxxlamp/ai-coding-config](https://github.com/wxxlamp/ai-coding-config), under `plugins/yuque-multichannel-publisher/`.

For me, the plugin has put the most tiresome transport work into a repeatable flow. After writing an article, I can keep my attention on the content, wait for local publication-package checks to pass, and then decide when to open each platform.
