---
title: Lessons from an Outsourcing Project
date: 2020-12-14 18:26
tags:
  - 技术管理
  - 测试与质量
  - 职业成长
categories:
  - 生活感悟
description: >-
  A school voting-system project that shifted from in-house development to a
  third-party service under time pressure, then encountered suspected vote
  manipulation that could not be investigated because the system was a black
  box.
lang: en
translation_of: an-outsourcing-experience
---

My bank internship was stress-free. I left punctually at six every day and lost the drive and enthusiasm for studying that I had at school. Around that time, the university needed a WeChat Mini Program voting system to select its ten most admired teachers. With time on my hands, I thought I might as well help: I could earn some money and practice by building a concurrent application.

<!--more-->

### The Beginning

At first, another student and I planned to build it ourselves. She would write the frontend in Vue, I would write the backend in Java and design the database, and we would define the APIs together. We could also study concurrent processing for a read-heavy and write-heavy workload, whose TPS we expected to reach 2,300. It seemed both challenging and interesting.

The voting system also had to prevent vote manipulation, another demanding problem.

Most importantly, this would be practical experience that tested the textbook interview knowledge I had memorized. The thought made me unusually excited.

But, yes, things never go that smoothly; there is always a “but.” My frontend partner told me she had found a company whose administration panel let users assemble a voting system themselves without editing code. If we used it, we would barely need to do anything. She also said the system was urgent and we might have less than two weeks to build it. After considering that constraint, we settled on the ready-made voting system instead of developing our own.

I regretted losing the chance to build it, but privately I was pleased that a few clicks would earn the money. Programming may be fun, but if you really want to make money, being the intermediary is the trick.

### What Happened

After choosing the solution, we contacted its vendor and paid several hundred yuan for a membership that covered our customization needs. Our frontend and backend roles turned into project-management roles. She reported progress to the teacher while I configured pages in the administration panel. The division of work was clear. What began as a challenging practice project became a naked money-making exercise.

**The teacher was our client, and we were the voting system's client.**

Before long, the school's teacher-selection campaign began and our twice-outsourced system went live. I felt nothing about the launch; it brought none of the accomplishment of releasing something I had built. At the time, though, I never imagined that such a small voting system would produce a farce.

### The Turn

Voting lasted five days, and nothing unusual happened during the first three.

Just when we thought everything was fine, votes began surging on the fourth day. By the afternoon of the fifth day, the leading teachers had four or five hundred thousand votes each, and the totals were rising visibly. The teacher kept calling to ask what had gone wrong and whether someone was manipulating the vote. I reassured her verbally, but inside I was panicking because I had no idea what was happening. I could only contact the vendor's support team. They insisted manipulation was impossible, but the votes were growing far too quickly and many IP addresses were repeated, so I too concluded that the vote had been gamed. I did not know how to answer the teacher because even if my conclusion was right, I had no way to fix it: the system was a black box to me. I had never seen its code, so I could neither identify the problem nor verify my suspicion. For the first time I felt that kind of powerlessness—not that I lacked ability, but that there was simply nothing I could do.

The teacher called incessantly on the fourth night. She thought I was the developer, but I was merely a messenger passing her words to customer support. It felt awful. I was a backend engineer, yet I could do nothing. I did not get home until nearly midnight—not because I had stayed late to write code or fix a bug, but because I had been answering the teacher and staring blankly at an administration screen.

### The End

The system closed on the fifth afternoon. I packaged the voting details for every teacher, including voter counts and times, and sent them to our teacher. She remained convinced that votes had been manipulated, while I could produce no evidence. An activity involving nearly one hundred thousand people across the university ended abruptly and inconclusively.

### Reflection

This was effectively a production incident. A voting event with more than a million participations failed, damaging the credibility of a school with over one hundred thousand students and staff. For the school, it was humiliating. Many comments under its official-account post condemned the activity and used it as an opportunity to criticize the university. I felt terrible: my self-interest had exposed the school to such public criticism. For several nights I tossed and turned, unable to sleep.

Vote manipulation was only my hypothesis. My client believed the enormous totals made manipulation highly likely, but neither the vendor's support staff nor I could provide evidence, so the event simply petered out.

The experience reminded me that future business development requires an owner's mindset and awareness of the whole system. Only then can I locate problems quickly instead of having strength I cannot apply. I must also evaluate the impact and consequences of business failure and prepare alternative plans and remedies.

If I ever have the opportunity to build a nationwide app used by many people, I must be exceptionally serious and careful. A single bug could affect hundreds of millions of people and cause immeasurable losses.

I originally thought this was a small matter. But do incidents not always grow out of small matters?
