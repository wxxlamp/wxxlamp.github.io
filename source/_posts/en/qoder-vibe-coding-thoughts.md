---
title: Reflections on Writing 10,000 Lines of Code with Qoder
tags:
  - AI 编程
  - 研发效能
categories:
  - 场景实践
date: 2026-06-07 16:00
description: >-
  Shares experience and reflections from using Qoder to develop 10,000 lines of
  code across two large commercial projects, examining the limits of AI Coding
  efficiency and how programmers' capabilities must evolve.
lang: en
translation_of: qoder-vibe-coding-thoughts
---

# Introduction

I previously used Claude Code, but recently could not use the Opus-series models for various reasons. With company promotion as well, I began using Qoder as its substitute.

In April I developed nearly 10,000 lines of effective business code. Human intervention during development was below 10%, although integration and test-submission required more human work because of infrastructure.

Through two key projects, this article discusses how much coding agents can improve R&D efficiency and what remains worth caring about in an era of organization-wide AI coding. The practical material is long; readers in a hurry can jump directly to the reflections.

I briefly record practices and thoughts from the coding stage. These lessons are not limited to Qoder; I hope to extract reusable strategies for other coding agents.

# Practice
## [Practice 1] Using Qoder to integrate a gateway payment flow with an external channel
> Under an existing mature architecture, this practice used the channel's mature API documentation to integrate five payment APIs and two webhooks.

### Development preparation

The PRD was not AI-native—it was not written in a structured form AI can understand. Feeding it directly to AI would produce a mess even with complete skills, MCPs, and rules. Before development, I therefore did the following:

1. **Clarified channel APIs:** understood call flows and timing, and special cases such as retries and idempotency; prepared complete API documentation for Qoder.
2. **Clarified the business solution:** after PRD review, many points remained undecided or conflicted with existing business, so people had to align the overall requirements with PD and the business team.
3. **Clarified the technical solution:** AI can write a design, but Qoder did not know the infrastructure's design preferences and priorities for channel integration. Letting it design directly from the PRD and documentation would cause much correction and rework. It was cheaper for developers to write the technical document's skeleton and cautions, then let Qoder complete it.
4. **Reviewed existing code:** channel integration is a mature gateway capability. Besides the design, PRD, and APIs, Qoder needed existing channel-integration code, including task-scheduling and API-rendering strategies. Do not expect it to understand code by grepping without context; that inevitably misses things.

### AI Coding stage

Before coding, I created a new-channel integration skill from prior experience. Combining it with SPEC completed design clarification, implementation, testing, and compilation.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/88836131_qoder-1.png)

Qoder fetched Yuque links, channel API documents, and related repository code from the technical document. Because the design was clear, its reasoning and output were highly accurate. It then asked about ambiguous points:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b74e18a5_qoder-2.png)

After clarification, Qoder generated a detailed SPEC. I spent about an hour reviewing it, correcting incorrect design, and asking Qoder to optimize it again:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/675c3786_qoder-3.png)

Once the SPEC was clear, Qoder could plan, implement, compile, and self-test autonomously.

<u>Although Qoder's design needed continuous clarification, it considered things that are hard to foresee during technical-document design. For example, its questions revealed that the original design for refreshing a new channel's token was wrong, enabling optimization.</u>

### Code Review stage

Even after repeated SPEC reviews, AI-generated code needs a code-level CR. I used both an independent-context CR agent with the technical document and manual visual checking, taking about two hours. Problems included:

1. Qoder's habits did not match my own, changing some style. For example, it wrapped every request and response in a `json object`; AI can understand this, but future maintenance may be difficult.
2. Its **architectural understanding** of the application was insufficient, so some architecture-related foundational code was not handled well.
3. The application used much Diamond and database configuration, yet **Qoder could not accurately obtain or add configuration**, creating many configuration-handling problems.
4. Repeatedly prompting AI to fix these issues can **pollute context and make Qoder fix things ever more incorrectly**, eventually requiring human intervention.

**In theory, a better harness can improve AI understanding of these issues. For item 4, subagents can reduce hallucinations caused by context consumption.**

### Self-test and fixes

After CR came self-testing. This could theoretically use MCPs for browser, HSF, database, and SLS configuration, but our infrastructure was incomplete, so testing remained manual.

1. Despite standardized documentation, the gateway did not correctly parse channel inputs and outputs. For a `data.response.result` response, Qoder omitted the middle `response` and parsed `data.result`, making channel data unavailable.
2. Channel error codes and idempotent retry mechanisms also need attention. Qoder handled error returns from the documentation but did not consider retries after errors or recovery cases.

<u>These fixes were difficult to request in the old context. Many integration bugs require repeated alignment with the channel before a solution emerges. In this stage, manual modification often proved much faster than AI Coding.</u>

## [Practice 2] Using Qoder for a fund-settlement integration in unfamiliar code
> This practice used Qoder and SPEC to write code for an application the developer did not know well. AI wrote 100% of the code, and delivery took about one week.

### Development preparation

As in Practice 1, although I did not know the application's architecture, I wrote a technical document from my own context and supplied it to Qoder+SPEC for design and coding. The document both let Qoder match the developer's thinking more accurately and helped me become familiar with the system. If the developer does not understand the system, 100% AI Coding is clearly extremely difficult today.

### AI Coding stage

I completed the core technical document manually:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0d21480a_qoder-4.png)

During SPEC, Qoder revealed a major design problem:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/0cfc6174_qoder-5.png)

1. Tax data had to be added. Under the existing business-code identity logic, the model needed two fields: tax amount and tax currency.
2. Because I did not know the code well, Qoder also identified the inflow and outflow direction of the tax fund flow during SPEC, avoiding many pitfalls.

### Code Review stage

After Qoder independently wrote the code and unit tests, I started a new agent for CR. It found country-validation issues: only Mexico may calculate tax; non-Mexico traffic should alert and be blocked. Since the codebase was small, around 500 lines, the new agent independently performed CR and fixes using the technical document.

### Self-test and fixes

End-to-end testing then found data inconsistencies through order processing.

**CASE 1:** Persisting data during order settlement failed because code fields differed from newly added database fields. Manual configuration changes differed from Qoder's understanding, causing database insert failure.

**CASE 2:** After partial order refunds, recalculating tax produced a settlement-total discrepancy that prevented settlement. Investigation showed that recalculating settlement after a refund did not handle the new tax fields. This was a knowledge-base and model issue, so Qoder had to be prompted to add the missing code:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/a6f6e234_qoder-6.png)

These problems show that insufficient context and reasoning information can skew Qoder's technical design. Human intervention and alignment are still necessary for non-code issues, or its coding will also go wrong.

# Reflections
## Use SPEC well

Qoder's SPEC mode is powerful: enable SPEC in the conversation and Qoder uses planning and subagents with existing MCPs and skills for Q&A before generating a spec document. Users should focus on reviewing and repeatedly revising that document through conversation to improve accuracy and delivery quality.

SPEC plus careful code review is at least twice as effective and efficient as simple conversational coding. SPEC consumes context quickly and it is unclear whether repeated compression will reduce quality, but Qoder's current compression is good and accuracy has not visibly decayed.

## Context determines everything

Modern coding agents compress context, but we still cannot complete unlimited requirements in one session. Claude Code's official documentation says to conserve context: results below 50% context usage are much better than those above 70%.

Context is always precious. Conserve it by:

1. **Using subagents:** a subagent has context independent of the main agent, which only needs its result, not its process. Careful inspection shows Qoder sometimes spontaneously uses subagents itself.
2. **Using skills rather than MCPs:** both consume context, but MCP only tells the model that a tool exists, while a skill's SOP is much more precise.
3. **Disabling unnecessary skills and MCPs:** do not load all system and personal MCPs and skills in every conversation; this consumes context and burdens the model with choices.

Use Qoder's repowiki to keep the system architecture current, and rules and hooks to update rules and handling. Repowiki and rules enter the model context in every session; only continuously updating them and maintaining the harness makes Qoder increasingly useful.

## Non-code configuration affects AI Coding efficiency

In the era of manual programming, everyone used non-code configuration to improve R&D efficiency. When a boss asks how efficiency improved, many answer, “What previously required code can now be done by configuration.”

Deployment and release are also extremely complex, and configuration helps changes go online quickly. But in an AI Coding era, when AI can write code almost instantly, do configurations scattered through Diamond, switches, and databases still improve efficiency?

They also create obstacles to AI understanding. Current infrastructure lets AI quickly read all code, but it is lost when configuration is involved: it cannot directly read configuration and therefore writes strange code. Without configuration permissions, developers also spend much time handling it themselves.

## Human participation is unavoidable

Many people reconsider the roles of humans and AI from architecture and top-level design. Extreme designs even imagine no people: AI handles requirements, coding, tests, and releases. It is a beautiful wish, but frontline practice in large commercial systems shows that end-to-end AI still needs time. AI Coding still requires expert experience and human intervention.

Simple class-level changes can unquestionably be fully given to AI. But people cannot fully state requirements during requirement design—not only PD, but developers too. Requirement creators cannot state every delivery need at once; therefore AI cannot be expected to directly write highly faithful, robust code. Today AI coding can join each atomic R&D stage and iterate code through Vibe Coding, but humans must still connect the entire software lifecycle.

Collaboration is another familiar issue. People say most R&D time is spent in meetings, not coding; similarly, much software-development time is spent in integration rather than coding. In the two deep Qoder practices, it wrote nearly 85% of code in the first SPEC stage, but the 15% needing integration fixes required people; Qoder could not handle it.

For channel integration, Qoder omitted defensive programming such as idempotency, retries, transactions, and consistency. These must be customized for different architectures, and developers must participate deeply for Qoder to produce expected code. This is not unsolvable: continuously improving project-specific coding habits and rules through the harness will reduce such intervention.

**Finally, if human participation is unavoidable, developers must still understand overall requirements, solution design, and code details. Would you dare deploy code you do not understand to serve users or operate funds?**

## Where are programmers' capability boundaries?

If the obstacles to full-lifecycle AI coding discussed above—model capability, context, and infrastructure—are solved, will programmers' job model change?

Certainly.

Programmers will no longer be constrained by languages: Java today, Python tomorrow. Once they understand a language's core ideas, models can supply syntax and ecosystem. Nor must programmers be constrained by specialties: frontend, backend, and big data can all theoretically be completed with AI assistance.

Does that mean programmers can do everything, and AI lowers requirements? I believe the opposite. AI frees programmers from rote interview knowledge and syntax so they can focus on transferable capabilities: learning, innovation, and rapid migration. They must understand more, make decisions, judgments, and guidance for AI in core domains rather than merely implement—because AI will certainly do implementation.

In the near future, programmers must master coding-agent tools as they master computing fundamentals, give code development to AI, expand their ability boundary upward, and engage deeply with business requirements and product capability. That is the most certain trend.

So if your present work never requires professional judgment and you only keep your head down coding, it is time to look up and reassess yourself.
