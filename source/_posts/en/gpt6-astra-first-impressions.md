---
title: "My First Day with GPT-6 Astra"
date: 2026-09-06 23:49:03
tags:
  - "AI 编程"
  - "大模型应用"
  - "开发工具"
categories:
  - "场景实践"
description: "A day using Astra to redesign my blog, discuss code, review changes, and spend fifteen hours trying to make a cycling video."
lang: en
translation_of: "gpt6-astra-first-impressions"
---
![An engineer checking a website and cycling storyboards by the window](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/f2ca3c53_cover.png)

After GPT-6 Astra launched, the PR was everywhere. I happened to be using Codex for development, so I wanted to see whether it was really as good as people said.

I spent all of Saturday giving Astra different tasks. My verdict up front: simply amazing. It felt great to use. Here is how that day went, from Computer Use and video storyboarding to code review, website development and UI design.

# 1. Website design and development

The first task I gave Astra was to improve my own blog, [SiBo's Blog](https://wxxlamp.cn/en/) ([Chinese homepage](https://wxxlamp.cn)). This was my prompt:

![My request to improve the website's layout and bilingual support](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/3bdd7134_en-source-01.png)

*English rendering of the [original Chinese screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/31975fbe_source-01.png), with the original crop preserved.*

As a programmer whose sense of design is, well, hard to describe, I could only give it a vague request to make the site look better. Nothing particularly complicated. Thirty minutes later, Astra came back with a result that surprised me. It designed, built and checked the site itself, then handed it over after the checks passed. That self-checking worked much better than what I had seen with Sol and other models.

I then asked for a few more changes to language support, layout, wording and SEO. A few words were enough for Astra to get what I meant and deliver the change. When I was using Claude Code six months earlier, this had felt almost impossible.

![Astra fixing the footer width](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/d2d73aac_en-source-02.png)

*English rendering of the [original Chinese screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/4152cda8_source-02.png).*

Here is the result. You can also visit the [old and new blog comparison](https://wxxlamp.cn/design-history/) to see the difference. The new version was built with Astra; the old one was built with Claude Code six months earlier. The comparison preserves the original Chinese pages.

![The previous blog design](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/ec090af0_en-source-03.png)

*English rendering of the [original old-site screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/0385b2c0_source-03.png); the layout is preserved.*

![The redesigned blog](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/3c74a781_en-source-04.png)

*English rendering of the [original new-site screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/9815efa2_source-04.png); the layout is preserved.*

One other thing: Astra's taste and ability to understand what I want feel like a huge step up from Sol. It also helped me prepare the content and layout of the WeChat article accompanying this post, including generating the images.

# 2. Discussing problems and writing code

Our team's AI work has recently been built on AgentScope, so I wanted to see whether there was an issue in the community I could fix. I found [issue #2373](https://github.com/agentscope-ai/agentscope/issues/2373).

I was pretty lost when I first read it, of course. I asked Astra to quickly walk me through the project's basic model, data flow and so on.

When we were discussing the problem and possible solutions, before getting into implementation, one word described Astra's responses: fast. Whatever I asked, it could generally give me the right conclusion within two minutes.

![Discussing the Discord Client architecture in AgentScope](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/ea7f3861_en-source-05.png)

*English rendering of the [original Chinese conversation](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/26c1217d_source-05.png).*

During that discussion, Astra and I even found another problem, [issue #2522](https://github.com/agentscope-ai/agentscope/issues/2522). It quickly set things up and reproduced that one too. It saved me a lot of time.

For this kind of work, though, Astra only felt a little better than Sol. I have not yet seen a leap in coding that went far beyond my expectations.

# 3. Code review and fixes

I also had a code review at work that I had not looked at yet. With Sol, the changes it made during a review often failed to meet my expectations. Time to see how Astra would do.

This involved internal company code, so I cannot show the actual review or fixes. Here is what stood out to me:

1. It understood my requirements more precisely. At the start of the review, I gave it a few points to focus on. Astra understood almost all of them and also spotted other compatibility problems in the code.
2. I have not seen a difference from Sol in coding ability so far. In complicated business scenarios, context engineering may matter more. A stronger model does not necessarily produce a huge improvement.
3. Automated acceptance checks were a little better. I used a simple prompt asking Astra to call the APIs and check the database after finishing the code, and it followed those instructions fairly well. But I still had to define the acceptance criteria clearly.
4. The Q&A was faster. As for usage, Astra felt a little more expensive than Sol. In the [official API price table](https://developers.openai.com/api/docs/pricing) on September 6, 2026, Astra's Standard short-context input and output prices were both 2.5 times Sol's. That does not translate directly into Pro usage limits, though.

# 4. Video scripts and storyboards

If Astra is this good at planning and checking its own work, could I get it to make a video from a single request?

I sent it a prompt asking for a video of a boy riding a bicycle from age 6 to 26, passing through the countryside, fields, primary school, secondary school, university and workplaces. I told Astra which schools and workplaces I had attended, hoping it could find pictures of them to use as backgrounds.

Off it went.

First, Astra found real photographs of the different locations and generated keyframes:

![Hand-drawn cycling keyframes for different stages of life](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/0408ad72_en-source-06.png)

*English rendering of the [original Chinese screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/b87756de_source-06.png).*

Then it used Blender with the keyframes to make test clips. At this point, Astra would check whether each video met the requirements and generate it again if it did not.

![A local cycling test and its remaining problems](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/141c2dbf_en-source-07.png)

*English rendering of the [original Chinese screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/2ad3d934_source-07.png), with the original crop preserved.*

I thought I could just sit back and get a nice video. But after 200 million tokens and fifteen hours, I had plenty of keyframes and short clips, and the video still did not meet my expectations. What Astra did better here was **planning, organizing and checking**. It could design storyboards and keyframes and inspect videos. Asking it to make the video directly was not a good idea. I practically burned through a week's Pro allowance. What a painful lesson. If you insist on making Astra produce a video, it will hunt down small video-generation models online, combine them with Blender and force out something that looks like it came from the 1980s.

Here are the approaches Astra tried:

| Stage | Actual method | What it achieved |
| --- | --- | --- |
| Initial 15-second version | AI images + JavaScript/Canvas animation | A finished video, but the rider-to-bike proportions and leg movements looked unnatural |
| Second version | Python controlling Blender | Built a 3D scene and movement, with some check renders; the complete film was not finished |
| Third version | Downloaded LTX-2.3 and ran it on my Mac | Generated several short clips with actual motion |
| 74-second storyboard version | FFmpeg editing | Mostly camera moves over still images, plus two model-generated clips of morning reading and office work |

So I tried a slightly unorthodox approach: have Astra use Computer Use to open the browser, sign in to Dreamina and make videos with the account's free credits. I even asked it to collect every free credit it could find:

![Astra collecting and using Dreamina's available free credits](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/7664f477_en-source-08.png)

*English rendering of the [original Chinese activity log](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/1d5ee885_source-08.png).*

Still, whether it was the prompt or the limits of Astra's capabilities, Seedance's free allowance was not enough. After spending a lot more Codex tokens, I was still unhappy with the video.

# 5. Computer Use

Most of the tasks above involved Computer Use in one way or another. I have to say, it works really well. It is also one of Astra's main features.

After the blog redesign, I wanted to improve its SEO and use Google Analytics to understand the traffic, but I had no idea how to configure everything. I gave Astra one instruction. It opened Google Search Console, Google Analytics and my DNS provider's website, then configured the necessary keys and code. Ridiculously convenient. Doing it myself before would have taken me at least two hours.

While reproducing the AgentScope issue, Astra used Discord in the browser to get the bot credentials. It also signed in to GitHub to create, comment on and claim issues. During code verification, it sent and received messages through Discord in the browser. It could reliably recognize what was happening on the page. Compared with my experience using Playwright a few months earlier, it felt like a different level altogether.

I am also having Astra split this article into posts for RedNote. You can find my RedNote account through [my blog](https://wxxlamp.cn/en/). The plan is to let Astra use Computer Use to open the browser, enter the creator center and fill in the posts. With Sol, there were usually little problems along the way. Astra now feels both fast and accurate.

For the video work, I also had Astra go straight into the browser after generating the storyboards and operate Seedance there:

![Using Seedance through the Dreamina browser interface](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/01fe398d_en-source-09.png)

*English rendering of the [original Chinese interface screenshot](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@e553be4c58969c0b47a33016c3624ae0d967d210/images/78e022ba_source-09.png).*

# 6. After a day with Astra

After using Astra, my reaction was: damn, this is good. **It is not that its coding ability has suddenly improved enormously; it feels closer to real-world work and reaches into tasks beyond coding.**

![Astra versus Sol: impressions from five kinds of task](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@39bcfed5bc8e47a03c472a624482ddccd8fa5001/images/7d1ce74a_en-astra-sol-observations.png)

Whether it was understanding what I meant, visual taste, computer operation, token use, self-checking or speed, it felt more than one step ahead of Sol. Of course, Astra alone does not deserve all the credit for these new capabilities. I might take a closer look later at how much Codex's memory contributes.

Without really noticing it, I have been using AI tools for several years. Looking back at these four years, from 2023 to now:

<section class="ai-years" style="margin:28px 0;padding:24px 20px 4px;background:#faf5f1;border:1px solid #eadfd7;border-radius:8px;">
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">2023</strong>I used GPT-3.5 to score the IELTS essays I wrote, saving myself some money.</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">2024</strong>I used DeepSeek to translate papers and help me read papers and understand code.</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">2025</strong>I used Qoder, Cursor and Claude Code for basic development—about <strong>20%</strong> of my code—and Gemini to help revise students' assignments.</p>
<p style="margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid #b58b72;line-height:1.9;"><strong style="display:block;font-size:22px;color:#7a4730;margin:0 0 5px;">2026</strong>Codex now delivers roughly <strong>95%</strong> of my code development, and I hand over all kinds of complicated computer operations to it as well.</p>
</section>

Large language models are often compared to a game of predicting the next word. But as capabilities such as tool use improve, AI has moved from answering questions toward connecting with the online world and carrying out the operations available there.

When I first started using AI tools, I would optimize prompts and manage the context to get better results. With Astra, I have found that I can simply give it a task and it will work through it itself. AI is moving far faster than I expected.

What will this look like in the future? AI may replace a lot of basic work. It may replace me too. But before that happens, I still want to see more of the world.
