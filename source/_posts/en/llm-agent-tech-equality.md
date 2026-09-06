---
title: How Large Models and Agents Are Democratizing Technology
date: 2026-01-10 15:42
tags:
  - 智能体工程
  - AI 编程
categories:
  - 业务学习
description: >-
  A Git branch-contamination incident illustrates how large models and agents
  can democratize technology, enabling non-specialists to solve complex
  technical problems efficiently.
lang: en
translation_of: llm-agent-tech-equality
---

I really do not know Git very well.

During campus-recruitment interviews, I could talk circles around interviewers and casually reel off commands such as `merge` and `revert` over the phone. But honestly, I had barely used them.

After more than four years of work, I still knew only the five basic moves: `pull`, `add`, `commit`, `checkout`, and `push`. I rarely encountered complex Git commands or collaboration workflows in daily work, so I had little motivation to study them carefully.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d951595f_f58e3da3.png)

---

But if you often walk beside the river, eventually your shoes get wet.

At around 10 p.m. last night, a teammate, Xiao A, committed and pushed the code for his feature branch as usual. After pushing to the test branch, he predictably encountered conflicts: with year-end approaching, no fewer than five feature branches had been merged into the test branch while awaiting deployment to the test environment.

This situation is common. Xiao A pulled the remote test branch, intending to merge his feature branch into it. Instead, with one slip, he merged hundreds of commits from the test branch into his own feature branch.

He did not yet realize how serious the situation was—or even that there was a problem—and continued committing code locally on his feature branch.

After several rounds of local commits, once he was satisfied that the code worked and prepared to `push` it to the remote test branch, he suddenly discovered that the test branch had contaminated his branch. His feature was due for testing and release the next day; he could hardly deploy everyone else's test code along with it.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/65798b24_d3d68755.png)

---

Xiao A began to panic.

Like me, he did not know Git particularly well. After struggling for an hour, he still could not remove the unwanted commits from his local feature branch.

With no better option, he created a new branch and `cherry-pick`ed his earlier commits onto it. By the time he finished, it was already past midnight. Exhausted, he took a taxi home under the moonlight.

The incident caused no major damage, but I was sure there had to be a way to remove the junk `commit` history from the original branch. The next morning, I opened GPT.

As I typed, “Branch A accidentally `merge`d branch B. How can I remove multiple `commit`s from B?” and prepared to press Enter, a thought occurred to me: “Could I just ask Claude to operate on it directly?”

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/26bf29ab_3e790e50.png)

---

That led to the following conversation with Claude.

Me:

> <font style="color:rgba(0, 0, 0, 0.88);">My Git branch accidentally merged another branch. Please roll it back to the latest commit whose committer is Xiao A.</font>
>

CLAUDE:

> <font style="color:rgba(0, 0, 0, 0.88);">Understood. I first need to find Xiao A's latest commit hash and inspect the current working-tree state.</font>  
<font style="color:rgba(0, 0, 0, 0.88);">The target commit is </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">commit_hash_A</font><font style="color:rgba(0, 0, 0, 0.88);">. I also found that an interactive rebase is currently in progress and has merge conflicts. To roll back safely, I need to abort the current rebase and then perform a hard reset.</font>
>

Me:

> <font style="color:rgba(0, 0, 0, 0.88);">Roll me back to this commit: a3a8f43dfa8eac801e804f76cf2c36450c717479.</font>
>

CLAUDE:

> <font style="color:rgba(0, 0, 0, 0.88);">No problem. I will reset HEAD directly to that commit.</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">Me:</font>

> <font style="color:rgba(0, 0, 0, 0.88);">Can you force-push my local branch to the remote repository?</font>
>

CLAUDE:

> <font style="color:rgba(0, 0, 0, 0.88);">Yes. I have confirmed that the current branch is </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">feature_1</font><font style="color:rgba(0, 0, 0, 0.88);">. Because we just rolled it back, the local branch is behind the remote and requires a force push.</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">Me:</font>

> <font style="color:rgba(0, 0, 0, 0.88);">The remote repository still contains the earlier merge commits and differs from my local branch. How do I remove them?</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">CLAUDE:</font>

> <font style="color:rgba(0, 0, 0, 0.88);">Let me compare the commit-history differences between the local </font><font style="color:rgb(38, 38, 38);background-color:rgba(0, 0, 0, 0.06);">feature_1</font><font style="color:rgba(0, 0, 0, 0.88);"> and the remote branch.</font>
>
> <font style="color:rgba(0, 0, 0, 0.88);">The analysis shows that although the local pointer is correct, the remote history contains many nonlinear merge commits automatically produced by the build system. We need to clean up the timeline.</font>
>
> <font style="color:rgba(0, 0, 0, 0.88);">Please confirm your cleanup strategy:</font>
>
> 1. **<font style="color:rgba(0, 0, 0, 0.88);">Completely discard</font>**<font style="color:rgba(0, 0, 0, 0.88);"> every commit after the target?</font>
> 2. <font style="color:rgba(0, 0, 0, 0.88);">Or </font>**<font style="color:rgba(0, 0, 0, 0.88);">retain</font>**<font style="color:rgba(0, 0, 0, 0.88);"> normal code commits after the target while removing only the merge commits?</font>
>

Me:

> <font style="color:rgba(0, 0, 0, 0.88);">I want to retain the normal commits after a3a8f43dfa and remove only the merge commits—the commits not made by Xiao A.</font>
>

<font style="color:rgba(0, 0, 0, 0.88);">CLAUDE:</font>

> <font style="color:rgba(0, 0, 0, 0.88);">Understood. This is a complex “rebase cleanup” task. </font>**<font style="color:rgba(0, 0, 0, 0.88);">Strategy</font>**<font style="color:rgba(0, 0, 0, 0.88);">: create a temporary branch from the clean commit, “pick out” (`cherry-pick`) Xiao A's valid commits from the old branch, append them to the new branch, and finally replace the original branch.</font>
>
> 1. **<font style="color:rgba(0, 0, 0, 0.88);">Create a backup and temporary branch</font>**
> 2. **<font style="color:rgba(0, 0, 0, 0.88);">Select and migrate Xiao A's commits</font>**
> 3. **<font style="color:rgba(0, 0, 0, 0.88);">Replace the main branch and push</font>**
>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/33d938e1_d745243d.png)

---

From asking Claude the first question to its completing the entire job took less than ten minutes. It was fast and effective. At that moment, I truly felt that technology had been democratized.

Our use of large models should not stop at conversation. With capabilities such as MCP and RAG integrated into agents, a well-written prompt can enable them to complete a great many tasks for us.

Inside the company, we have also used large models and coding agents to generate code autonomously. Many teams are actively exploring autonomous ticket diagnosis, integration testing, and other capabilities based on large models and agents.

Individuals should likewise use agents to automate routine chores. Our working model may eventually change: learning how to talk with an agent and supervise it may become an important subject.

The foundational capabilities of large models—what we usually call pre-training—matter greatly. Some people say post-training matters too, and I do not disagree. **In the consumer market, however, agent capability will be the decisive factor for many AI products.**

I believe that helps explain why Meta spent a billion dollars acquiring a company that did no model training and focused only on agents. It also helps explain why Alibaba's Qwen, despite becoming the leading open-source model worldwide, still cannot outperform Doubao in the consumer market.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5599e669_fb6d2a35.png)

---

Finally, returning to today's topic: how can you quickly remove a branch that was merged into your Git history? See the image below.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/94da7da8_f317e49c.png)

> Note: the images in this article were generated with Gemini Nano Banana Pro.
>
