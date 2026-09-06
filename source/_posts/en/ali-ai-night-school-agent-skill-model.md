---
title: 'Agents, Skills, and Models: Reflections from Alibaba AI Night School'
tags:
  - 智能体工程
  - 大模型应用
  - 系统设计
categories:
  - 架构思考
description: >-
  Drawing on Taotian Technology AI Night School and Agent-development practice,
  this article discusses the boundaries among models, Agents, and Skills, along
  with business choices and evaluation methods.
lang: en
translation_of: ali-ai-night-school-agent-skill-model
date: 2026-08-18 23:29:47
---
![Engineering thoughts after an evening AI class](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/60fce5c0_cover.png)

# 1. Preface

![From AI Night School to seven Agent engineering questions](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/1bbb01e7_section-1-v2.png)

I recently attended AI Night School training organized by Taotian’s business technology organization. As I have been working on Agent-related development lately, I enrolled in the two-month course. Last Thursday’s first overview session was excellent, and I want to combine my recent experience building Agent applications with some thoughts on Agents, Skills, and models.

This article has been declassified and contains no commercial secrets. It is highly personal in its thinking. Some sections assume readers understand the basic concepts of LLMs and Agents; without that experience, they may be a little demanding to read.

# 2. Can Agents replace everything?

![Probabilistic models and deterministic programs complement each other in production systems](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d544d05d_section-2-v2.png)

From Agents emerging in 2024, to their concentrated explosion in 2025, to xxClaw triggering “everyone raising shrimp” in 2026, LLM-powered AI appears able to do anything. Quite a few AI bloggers even make the bold claim: “In the future there will be no software, only AI.”

Reality is not that tidy. Many people have never used office Agents such as WorkBuddy, Manus, or QwenWork, and their understanding of AI remains at the level of chatting with Doubao. Even if monthly active users of office Agents truly grow from millions to hundreds of millions, can AI replace all SaaS software?

From a software-engineering perspective, I think that conclusion is overly optimistic.

An LLM can be roughly understood as an enormous “idiom-chain game” system. Even top algorithm researchers currently struggle to clearly attribute every output. When calling an LLM, even with `temperature` set to 0, multiple responses may not be entirely identical. Difficulty of attribution and uncertain output are unavoidable characteristics of models. Model capability alone has difficulty directly taking on highly sensitive, high-risk business operations.

The real change LLMs bring is the ability to handle unstructured data. After training on massive data and parameters, they seemingly understand almost every kind of natural-language expression and give reasonable feedback. This happens to be what traditional structured programs are not good at. Workflows that once required users to repeatedly operate across multiple interfaces can be turned into more natural conversational interaction through an LLM, but that does not mean existing software will be completely replaced.

In production applications, AI and programs are more like complementary roles. Models understand fuzzy intent and handle unstructured information; programs perform deterministic and structured operations. A simple example is that production environments commonly equip LLMs with a calculator tool to calculate directly. Models can calculate too, but calculator results are more stable, cheaper, and easier to verify.

Cost is also very real. Context and Tokens are not cheap. Assigning a deterministic task to a normal program may consume little CPU and memory; giving every step to an LLM significantly increases resource cost and response time.

Of course, one can think more aggressively: if deterministic programs themselves are written by AI and then called directly by AI after being written, does that mean AI can ultimately take over the whole digital world? In one sense, it can be understood this way, but the process will be very long. Complex software architecture and continually emerging incremental requirements remain difficult to automate completely.

# 3. What is the essence of an Agent?

![The three-layer responsibilities of Model, Agent, and Harness](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/8cffabe2_section-3-v2.png)

While browsing the Jike community previously, I saw many bloggers with “xx_AI” in their names evaluating new models such as DeepSeek, MiniMax, and GLM. Some even judged whether a base model was capable by “how many Subagents it starts” or “whether it can generate attractive videos.” The latter at least corresponds to multimodal capability; the former is strange: starting multiple Subagents is an engineering implementation, not a base-model capability.

So what is an Agent? Where is the difference between an Agent and a Model?

For models, refer to my [introductory LLM article](https://wxxlamp.cn/en/2025/12/24/ai-ml-getting-started/) from last year. Put simply, the core of a model still resembles an “idiom-chain game”: based on enormous parameters, it uses vector and matrix operations, takes Prompt Tokens as input, and progressively generates output. Multimodal models work similarly, except their inputs and outputs become specially encoded image, audio, or video Tokens.

Anyone who has read the source code of open-source Agent tools such as Codex and OpenCode will find that an Agent is essentially an engineering wrapper around calls to a model API. It assembles user input, descriptions of tools and Skills, system information, and other content into context and sends it to the model API; the model then returns Thinking Delta, Text Delta, and the tool name and input parameters to execute, token by token.

An Agent’s value lies in uniformly managing the runtime for LLM API calls and providing invocation patterns such as ReAct and Handoff externally. Developers mainly focus on an Agent’s Prompt, Tool Config, and Skill, without repeatedly adapting to protocols and parameters of downstream model interfaces.

One layer outward, the boundaries of today’s large Agent platforms have gone beyond a single Agent and are closer to a Harness suite. Beyond model invocation and context assembly, they handle memory extraction and storage, state restoration, tool execution, and even self-iterative optimization. These are all parts of Harness engineering.

Developers need not obey the Agent abstraction in every scenario, however. Sometimes we only want to customize one model-interface parameter; having to create a whole Agent Prompt, Tool, and Skill is somewhat like using a cannon to kill a mosquito. Abstraction should resolve complexity, not create it in reverse.

Many base models emphasize their Agentic capabilities. An important reason is that during training they encountered massive amounts of data in formats such as Function Call, Thinking Delta, JSON Schema, and System Prompt. Thus, once in an Agent environment, they more easily generate tool-call information that meets conventions. Such models are usually called Agentic Models. Tool-orchestration approaches, the number of Subagents, and runtime recovery capabilities still belong to engineering systems outside the model.

# 4. Thoughts on Skills

![Engineering choices among Programs, Skills, and Subagents](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/e9159408_section-4.png)

At the beginning of this year, after Anthropic proposed and popularized the concept of Skills, many friends—especially those who do not develop software—felt that everything could be solved by writing a Skill.

When talking with product colleagues, I often hear: “Quickly abstract this into a Skill, then I will not need to ask you again.” There is a correct part to that statement, but also an obvious boundary. Skills can indeed accumulate experience, but many problems will not resolve themselves simply because a Skill has been written.

Anyone familiar with Agent development knows that a Skill is essentially a working SOP. To prevent model context from becoming overloaded, Skill content is usually loaded progressively. A Skill can therefore be viewed as a larger, more structured Prompt. In essence it is no different from instructions typed into a Doubao input box; the principal difference is that its full text is not inserted into context at the beginning. Instead, it is progressively loaded based on the task, saving context and reducing interference with reasoning.

Since a Skill describes an SOP, can everything be made into a Skill? Theoretically yes; in practice, there is no need.

We should not repackage every existing SOP and Workflow as a Skill just for AI. On the one hand, programmatic Workflows cost little to execute and are more stable. On the other, the same Skill in different Agents is affected by context style, base-model capability, and recovery mechanisms, making results hard to make as precise as program flows. Skill text is deterministic, but execution results still carry model uncertainty. The market also currently lacks sufficiently mature, unified tools to evaluate and optimize Skills. The road to precisely using Skills at scale is still long.

Another easily missed issue is that an Agent can read a Skill in full. Opening a Skill is, to some extent, exposing all accumulated experience within it. This risk cannot be ignored when sensitive experience or internal knowledge is involved.

Therefore, for most deterministic tasks, replacing programs with Skills is often merely “AI for AI’s sake.” For example, uploading an image to GitHub can call the GitHub interface directly through a script, or use a Skill to have a model operate a page through Browser Use. Clearly, the script is faster, more stable, and more trouble-free.

Skills are better suited to business processes that cannot be fully programmed but whose operational experience can be summarized. They can combine MCP and tools for overall orchestration. For example, in a handover scenario, a colleague about to leave can organize an operating manual as a Skill, and the incoming colleague can then use AI to complete tasks that previously required repeated questions. The value here is making tacit experience executable; deterministic steps still go to programs.

There is another, more technical question: what exactly is the difference between Subagents and Skills? For nontechnical colleagues who directly use Agent tools such as WorkBuddy, this may sound odd—Subagent is an Agent, Skill is an Agent’s SOP, so why compare them?

From an engineering implementation perspective, Agents and Skills both ultimately become sets of context passed to the model interface. Thus actual development often faces the same choice: should a task be placed as a Skill in the primary Agent, or assigned separately to a Subagent?

My judgment is that Subagents suit tasks that can be completed independently, need independent context, or can run in parallel. A primary Agent plus Skill suits general flows requiring continuous shared context. When using Subagents, pay special attention to how intermediate artifacts are handed off; otherwise the benefits of isolated context may become information loss.

# 5. Common business scenarios for Agents

![Agent scenarios in development, service, learning, and requirement understanding](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/a37b6bc8_section-5-v2.png)

The discussion so far shows that Agents can hardly replace software for all work; having Agents also does not mean business revenue and profit will grow naturally.

Agents are first and foremost efficiency tools. They can help programmers with end-to-end development from requirement understanding to code implementation, and help nontechnical colleagues investigate tickets, process Excel, and write weekly reports. More importantly, many of these tasks can run in parallel. Work that is highly standardized but complex to process can go to Agents, leaving people’s energy for the parts requiring judgment and creativity.

Because they can handle large amounts of unstructured data, Agents are also naturally suitable for customer service, sales, and QA. New-hire landing and work handovers are common scenarios as well. I saw at WAIC that financial systems are nearly all experimenting with Agent-based Q&A customer service. These practices still sound early-stage, but the direction is straightforward: first connect scattered knowledge and operational processes, then progressively raise task-completion rates.

Learning is also very suitable for Agents. An Agent does not lose patience due to repeated questions, can adjust explanations to learners’ understanding levels, and has broad enough knowledge coverage. Knowledge accuracy and teaching pace still need evaluation, however, especially in specialized domains where fluent answers cannot simply be assumed correct.

Moving further toward algorithms, LLM reasoning can be used to understand user needs more finely, supplementing information traditional structured features struggle to express. This can form more detailed user profiles and then serve search and recommendation scenarios.

At present, the more certain value of most Agent scenarios is still efficiency improvement. Teams hoping AI will directly relieve all business pressure may need first to re-examine their business model: does the problem come from repetitive work, information processing, or the product itself? Placing every expectation on AI makes it easy to miss the problem that should actually be solved.

# 6. Agent-development choices and considerations

![Trade-offs in Agent development among runtime location, flows, and interaction](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b16dbcdd_section-6.png)

For technical colleagues, many specific business needs cannot be completed directly through general desktop Agents such as WorkBuddy and QwenWork. It is often still necessary to call model-vendor interfaces and manage context independently. In this situation, several matters need to be thought through first.

First is whether the Agent runs locally for the user or in the cloud. With local operation, message disconnection and service recovery are relatively simple. If it runs in the cloud, exceptions such as message disconnection, server restarts, system outages, context storage, and scenario memory must be handled. The cloud also has obvious advantages: it can centrally collect user data and run business 24×7. Many vendors have recognized this; Alibaba’s earlier MuleRun and Qoder Agent Cloud are products that package Agents in the cloud for users to call through APIs.

Second is the choice between ReAct and Workflow. Nearly all current general Agents show traces of ReAct, and implementations such as Codex (OpenAI also open-sourced a framework with the same name), DeepSeek Harness, and AgentScope have appeared. ReAct lets a model autonomously call tools through “thought—action—observation,” making it suitable for open problems. But ReAct alone is often insufficient, and developers still need to provide more deterministic Workflows.

The advantage of Workflow is high determinism, more controllable cost, and faster execution. A common approach is to have ReAct first generate a Dynamic Workflow, letting AI decide the flow, then handing execution to a program. The common Plan pattern can also be seen as a variant of this form. During actual selection, clearly separate “what the model decides” from “what the program guarantees.”

When truly writing an Agent, context management, memory, and caching are also important. How should user and system messages be positioned and inserted? When should user memories be extracted? Where are memories stored and how are they retrieved? How should context be assembled to make better use of Model Cache? How should tool inputs and outputs be compressed? How should every session be managed? These questions are difficult to solve completely with one unified framework, and usually must be designed one by one with the product form in mind. I only list the questions here; I may expand on particular solutions later.

Finally, do not become constrained by Chat when developing Agent applications. Using a chat box does not mean a product is more intelligent. Agents truly excel at handling unstructured information and understanding fuzzy intent; interaction should still begin from the product perspective: when a button clearly solves something, why force the user to type a paragraph?

# 7. How to evaluate Agents

![A closed loop of Agent runtime metrics, business standards, issue diagnosis, and historical regression](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/7e849ca7_section-7.png)

In traditional software engineering, development and testing are both important stages; Agent development likewise cannot do without evaluation. Verifying that an Agent can complete basic functions is only the first step. The harder questions are whether it is actually useful in unstructured scenarios, can be used stably, is worth using, how Bad Cases can be found, and how problems can be quickly located and optimized after they appear.

I think Agent evaluation must solve at least three problems:

1. Basic functions: ensure the Agent’s product functions meet business requirements.
2. Stability: cover different inputs, different times, and every kind of Bad Case, checking whether output consistently meets expectations. LLM output is probabilistic, so evaluation cannot rely only on one manual experience; Agent evaluation needs to be as automated as possible.
3. Optimization suggestions: beyond showing whether an Agent meets expectations, evaluation results should locate places to optimize in the execution chain, such as Prompt, Cache hit rate, Skill, or tool description. It is best to evaluate the cost of each execution too, to determine whether real ROI meets business expectations.

To accomplish this, an evaluation system also needs several foundational capabilities:

First, collect runtime metrics such as `cache hit rate`, `TTFT`, `token cost`, and `time cost`. Without them, it is difficult to judge whether an optimization improved results or merely increased cost.

Second, design evaluation criteria around business expectations. Agent output is difficult to measure with a single universal score; evaluation items must answer whether it completed a specific business goal.

Third, identify and locate Bad Cases. After finding results that fail to meet expectations, continue determining whether the problem lies in Prompt, Skill, tool, context assembly, or the model itself.

Fourth, retain historical evaluation results so every change can be traced and associated with previous versions. Otherwise, after adjusting a Prompt or Skill, it is easy to fix the current Case while bringing old problems back.

For now, this section is more a summary of problems and directions. This article does not yet expand on concrete evaluation implementation. Once later practice is more complete, I will write a separate article.
