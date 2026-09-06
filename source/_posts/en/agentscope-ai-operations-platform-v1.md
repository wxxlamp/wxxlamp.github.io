---
title: Designing an AI Operations Platform with AgentScope
date: 2026-07-19 23:58
tags:
  - 智能体工程
  - 大模型应用
  - 系统设计
categories:
  - 架构思考
description: >-
  Summarizes engineering practices for an AI operations platform built on
  AgentScope, covering prompts, state machines, parent and child agents, tool
  governance, integration validation, and user-experience improvements.
lang: en
translation_of: agentscope-ai-operations-platform-v1
---

![AI operations platform](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/52d30cd1_agentscope-ops-platform-cover.png)

> When many people begin agent development, their first instinct is to make the agent loop run: the model calls a tool, gets a result, and enters the next round. But once you make an operations-oriented AI platform genuinely usable, you find that the loop is only the starting point. Based on AgentScope, this article discusses the things we encountered and considered while building an AI operations platform beyond the loop: how prompts and skills divide work, how to guide long flows, and how to ensure parameter correctness across multiple downstream APIs. (Internal platform URLs, system names, and concrete business data have been removed; only reusable engineering practices remain.)

## I. Core problems and solutions

Three core problems are unavoidable in this type of operations agent; the approaches we ultimately adopted are listed alongside them.

### Core problems

1. How can strategy defined by algorithms be effectively recognized by the model?

    - Split agents by domains such as audience selection, outreach, and benefits; each domain agent maintains its own context and skill.
    - Use AgentScope to implement the agent loop and basic skill and MCP management.

2. How can long operational flows be guided correctly without taking arbitrary actions?

    - workflow + frontend flow rendering
    - ask user question cards

3. How can multiple downstream systems be connected while ensuring parameter correctness?

    - Connect marketing-delivery platforms, outreach platforms, data warehouses, low-code platforms, collaboration documents, and other tools and MCPs.
    - For tools such as coupon delivery and outreach, extract and parse core parameters from context rather than letting the model fill them in itself.

### Architecture and solution

The following is a sanitized overview of the architecture; you can compare it with each module discussed below:

![AI operations platform architecture](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/fc72e4a1_agentscope-ops-platform-architecture.png)

## II. Prompts, skills, and conversations

### Thinking about the division of work between prompts and skills

When you are starting out, you will probably do as we did: keep the main agent's prompt simple and put routing and workflow management in skills. Soon, however, you discover that the model sometimes does not load the relevant skill at all. It instead improvises from the system prompt, weakening the result. Two recommendations follow:

1. Skills are disclosed and loaded progressively. If data is important and used in every round, put it directly in the system prompt. Do not put it in skills merely to save tokens, or the effect will suffer badly.
2. Although system prompts are often recommended to stay within roughly 500 lines, do not be constrained by that at the start. Write a broad, comprehensive system prompt first; once results stabilize, optimize its length through references.

### Dynamic prompts prevent Lost in the Middle

For Transformer-based LLMs, attention tends to spread toward both ends and information in the middle may be “forgotten.” Compression can also remove tool results from an agent. Remember one principle: do not leave truly important information for the model to manage by itself; intervene manually.

Using AgentScope middleware, at the beginning of every turn we abstract important information from memory and forcibly append it to the system prompt with `<Context-Reminder></Context-Reminder>` tags. This ensures the model gives critical information “absolute attention.”

Context-Reminder normally includes:

`Basic campaign information (campaign name, user ID, and so on), campaign stage and flow control, audience information, IDs from external APIs, and so on`

### How to optimize prompts

Our prompt-optimization rhythm has three steps:

- step1: Write the initial prompt according to the agent's role and function.
- step2: Keep adding prompt content and get the effect working first.
- step3: Once the effect meets expectations, store parts of the prompt in references and load them progressively.

Two cautions:

1. Prompts do not need to concern themselves with tool input parameters.
2. Do not compress prompts blindly just because of context length.

Further reading:

1. [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
2. [prompt-eng-interactive-tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

### Context compression

Overlong context both slows model reasoning and affects reasoning quality. AgentScope's default compression strategies currently include compressing thinking, tools, and model replies. You can understand their progression this way:

1. With AgentScope, the model's thinking process and tool-call results are compressed by default, retaining only the user's and model's Q&A in each round.
2. A more advanced compression strategy retains some tool results while removing invalid conversations.

## III. State machines and the Plan tool

An operations campaign is often complex and long-running: it must answer user questions flexibly while guiding the user through the process. We therefore dynamically inject a state machine into the system prompt, which guides the user at the highest priority. One key detail: do not write state-machine rules into the prompt. Instead, use hard code to determine the model's current step and what it must do next. Its overall form is:

```json
{
  "currentStage": "阶段标识",
  "currentStep": "当前步骤标识",
  "nextStep": "下一步骤标识",
  "actionType": "independentThinking | callSkill | callAgent"
}
```

Along with the current step, explicitly tell the model whether completing it requires independent thinking, calling a skill, or calling an agent.

To let steps advance dynamically, we customized a plan tool. The model calls it after completing each step to update progress. The system detects memory-data changes and, in the next loop, feeds the latest step back to the model through middleware.

Because these steps are persisted in a database, operators can see the workflow progress directly in the frontend, greatly improving the experience.

## IV. Parent and child agents

### When should you use a child agent?

First dispel a misconception: an agent is essentially a contextual wrapper around a model API, and the model cannot actually recognize a “child agent” (to it, that agent is merely a tool). Compared with a skill, however, a child agent has an independent context and can execute concurrently. Decide whether to split out a child agent using these three criteria:

1. Is the subtask independent?
2. Can the subtask execute in parallel?
3. Does the subtask require too many iterations?

**Division of work** also brings an easily overlooked organizational benefit. When several algorithm engineers participate, splitting child agents by domain lets everyone own the quality of their own agent. Clear domain boundaries make integration smoother and provide better assurance for the whole project.

### Communication and collaboration between parent and child agents

Three practical lessons:

1. Dynamically inject the “child agent currently to be called” into the parent agent's system prompt. This prevents the parent agent from taking over before the child task is finished and significantly improves the parent's recognition accuracy.
2. Require child agents to return JSON and add an `isCompleted=true` field to indicate completion. (Some models can enable structured JSON output by parameter.)
3. After a child agent finishes, persist its returned result through middleware. Because the JSON format is fixed, the data can directly become inputs to subsequent tools.

### Optimizing excessive reasoning time

During initial tests, agents can take too long to reason. Do not simply disable thinking: that severely harms results. With LLMs, we took several measures to reduce reasoning time:

1. Context compression: remove child-agent skill preloading and lower the main agent's thinking-token limit.
2. Thinking budget: some LLMs expose a `thinking-budget` parameter to control thinking duration.
3. Adjust top-p and temperature.

We are continuing to explore several directions:

1. Parallel agent invocation.
2. Asynchronous agent invocation, with the main agent returning results to the business early.
3. Splitting agent responsibilities more finely and matching different models and parameters to different responsibilities.

## V. Tools and MCP

### How to ensure API-parameter correctness

When integrating APIs such as marketing-delivery and outreach platforms, the greatest concern is that the model will not understand parameter meanings and therefore pass incorrect parameters, such as channel ID, validity period, or start time.

Experience confirmed this concern. In early integration testing, the model regularly passed wrong fields; audience SQL was a typical case. Even if field definitions are clear, when many audience-selection SQL statements exist in context, the model may randomly choose the wrong one—for example, pass a production table instead of an offline table, or use a benefits SQL statement for outreach SQL.

We adopted three measures:

1. Add a “parameter definition” API on the delivery-platform side to strictly constrain input enumerations and make definitions as rich as possible.
2. On the operations-platform side, wrap the delivery platform's MCP as tools, then use middleware to hard-code extraction of key parameters—audience SQL, start time, validity period, campaign type, and so on. Code passes these parameters directly; the model does not need to infer them.
3. Add monitoring: persist both the “model-inferred parameters” and the parameters ultimately passed to the delivery platform, making later audits and tracing possible.

### Pitfalls in concurrent tool calls

Calling tools concurrently can reduce model loop count and improve results, but be careful: concurrent modifications to database fields may overwrite data and break consistency. Evaluate this before designing a concurrency plan.

## VI. Integration and validation

After changing a prompt or skill, validating the corresponding feature is often time-consuming, and it is difficult to know whether the change affected other areas.

Our solution is a custom script. It uses a coding agent to call the platform's chat API, converse with the platform through a model, and intelligently judge whether the platform's reply meets expectations under agreed constraints. The validation uses these artifacts:

1. An e2e script that converses with the platform through a coding agent.
2. Output from platform conversations.
3. Platform runtime logs.
4. The platform model's context (only the final two arrays).

Feed those artifacts to the coding agent and ask it to analyze whether platform behavior meets the standard in light of the feature optimized this time.

Frankly, this approach is still early. We have automated the conversations, but because agents in different roles are all specialized, algorithm engineers still need to combine the logs for final analysis after the conversation ends.

## VII. User-experience measures

### KeepAlive mechanism

When a user does not provide input for a long time, an SSE stream can easily disconnect. We added a server-side keepalive mechanism to prevent conversation interruption. If your product also uses SSE for streaming output, this is almost essential.

### Resume-and-retry mechanism

Network jitter, such as backend-service deployment, can break chat. We therefore added resume-and-retry support in the frontend: it automatically retries a chat session three times, minimizing user awareness.

### Ask User Question cards

Using AgentScope, we optimized ask user question cards. After the model calls this tool, users can choose options directly, fill blanks, and complete dates, yielding a smoother interaction.

## VIII. Future development and plans

Finally, here are several directions we are advancing; discussion is welcome:

1. An auto copilot for multiple products and campaigns.
2. An automatic correction mechanism for different campaign types derived from user sessions: use scheduled tasks to scan user conversations, capture what users question, and automatically optimize skills and prompts.
3. Invoke different agents concurrently to improve system response speed.
