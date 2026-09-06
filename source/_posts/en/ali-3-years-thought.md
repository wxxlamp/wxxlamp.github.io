---
title: 'Three Years at Alibaba: Personal Reflections Beyond Technology'
date: 2025-02-16 20:19
tags:
  - 职业成长
  - 技术管理
categories:
  - 生活感悟
description: >-
  A non-technical retrospective after three years at Alibaba, sharing genuine
  reflections from a campus hire on balancing business and technology, project
  management, workplace mindset, and embracing change.
lang: en
translation_of: ali-3-years-thought
---

On July 9, 2021, I joined Alibaba as a campus hire and began a journey there that has been both fascinating and meaningful.

Over these three years, I moved from the Corporate Finance Technology Department to ICBU Technology, with a stint seconded to 1688 Technology in between. Apart from the now-defunct LST business, I seem to have experienced nearly every line of business in the Binjiang campus.

I went through five managers and changed teams countless times. There were plenty of good and bad moments, and all sorts of frustrating, maddening situations. Fortunately, the experts around me helped me patiently and taught me tirelessly. They let me feel the warmth of Alibaba people, and I gained friendship, growth, and moving memories here.

There is a saying at Alibaba: “three years to become an adult.” At this point, I would like to offer a small summary. Criticism is welcome~

## Working on Business and Doing Technology
“You build rockets in interviews, then tighten screws after joining.”

In today’s increasingly competitive environment, interviews have become harder and harder. HR screens résumés first: no non-985 candidates, no candidates without projects. During interviews, most Alibaba interviewers begin with a few standard theory questions, assess your ability through the projects on your résumé, and finish with some high-concurrency questions. After taking that combination punch, candidates really believe their future work will be closely tied to high concurrency and high availability. They imagine taking on tens of millions of concurrent requests and billions of users, thrilled at the thought that transaction after transaction would be completed through code in their hands.

But after joining, they discover that all the high-performance and high-availability tricks they wielded so easily in interviews have no place to be used. Instead, they get pushed around by PDs and grind through CURD. Every day, they guess at ancient business details buried in mountains of legacy code written years ago. One mistake can earn them a P-level incident, followed by a group chat and a full postmortem. A major blunder can mean an N+1 package and a direct trip back to society.

Many people join business teams and then find that the code they work with daily—perhaps under pressure from rapid business iteration, perhaps constrained by flaws in a predecessor’s design—has almost no “technical” design to speak of. Adding machines or upgrading configurations at the first sign of trouble is the most common, and perhaps the only, way to deal with so-called high concurrency.

As for high availability, the middleware platforms are already mature enough that the extreme problems mentioned in interviews are unlikely to occur. Even if they do, they fall outside the scope of business scenarios: the data volume is too small, and offline reconciliation and correction is often the usual solution.

So after joining a business technology team, I believe most campus hires, after developing business requirements for a while, either start questioning the company and sigh, “Is this all Alibaba is?”, then numb themselves and let requirements push them forward; or suffer a deeper collapse of conviction, begin doubting their original dreams, and eventually either get pushed out or leave for another field.

---

I belonged to the first group when I had just joined. Watching classmates around me blast through CURD tasks, I could not help feeling lost and questioning the meaning of the three years I had spent studying technology at school. I often wondered: could doing CURD every day really solve problems?

Pure CRUD certainly cannot solve problems. As I went deeper into the work, I found that things were far less simple than I had imagined. Although it is still create, read, update, and delete, the prerequisite for writing it is a substantial understanding of the business. Only by abstracting and modeling real business through technology can we write highly extensible code. As we take on more and larger requirements, the business knowledge we gain gradually becomes our own moat. Along the way, we write code that is more robust, readable, and extensible. The business knowledge we master, along with the performance and stability targets the business currently needs, all become valuable professional assets.

The biggest difference between business technology teams and pure technology teams is that they solve different problems. Business teams solve real-world business problems, while pure technology teams solve technical problems. To some extent, computer science students with formal training are more easily influenced by geek culture: they believe that after graduation they will certainly do a great deal of technology-related work. Combined with the hard-core questions asked in interviews, this raises expectations and creates a large sense of disconnect once people start working.

In a business team, a major taboo for technologists is showing off technical muscle for its own sake. Everyone wants to try new technologies and harder challenges. But if low concurrency can solve the business problem, why invite pain by tackling all the problems of high concurrency? Especially in today’s environment of operating responsibility, technology’s job is to serve the business and solve business problems at the lowest cost.

---

Still, knowledge is everywhere if you pay attention. Although many hard-core technologies are not useful in day-to-day business scenarios, there are plenty of opportunities to learn after joining Alibaba if you truly enjoy studying technology: read middleware source code, apply middleware design patterns, solve the strange problems you encounter every day (Maven dependency conflicts, class loading), respond to and handle production incidents, and so on. As long as you make time, even if you are tightening screws on a business team, the chance to build a rocket for the business may come if you prepare a little more.

## The Courage to Borrow Arrows with a Straw Boat
While writing this article, I searched with GPT and found that introverts may account for 60% or more of programmers. This personality trait can certainly help people focus more during development, but it often also makes developers less proactive in communicating with others.

When many people first join, whether they are learning the business or developing a requirement, they feel embarrassed to ask senior colleagues when they run into problems. Some even mumble that a project is nearly done when a senior asks for progress, only for joint debugging to reveal that their code differs considerably from what the business expected.

Therefore, for campus hires, asking senior colleagues, managers, and business partners questions at appropriate times is essential to maintaining the pace of growth. Yet people often lack the courage to ask. Based on my own experience and examples around me, the usual reasons are roughly these:

1. They have never interacted with the person they want to consult and do not know how to start;
2. They worry the question is too simple and fear being laughed at or looked down on;
3. Everyone is busy, and they worry about disrupting the other person’s work.

Another example left a deep impression on me. A few years ago, a newly joined campus hire in the team next to ours was still working at his desk at 11 p.m. I was also dealing with a few things, and since he had not left, I went over and chatted with him. I learned that he was dealing with a very classic Spring startup issue, so I helped him solve it. Later I found out that he had already been looking at it for almost three hours. If he had found a chance to ask other classmates for help, he could have been in bed launching Genshin Impact at 11 that night.

It is not only about asking other people. Alibaba has so many technical assets. When you hit a problem, searching Yuque or ATA often gives you a 50% chance of solving it. Learning to use tools is also part of growth.

---

Unlike ancient times, when a household could nearly complete the entire chain from production to consumption through farming and weaving, modern society is founded on specialization and cooperation. So dealing with other people is unavoidable. Very often, our own work can only be completed by actively or passively relying on others’ help.

When new colleagues first enter the workplace, they should draw more on the strength of senior colleagues and peers. During the beginner-protection period, people are more tolerant of the things you do not know. So while you are at your most inexperienced, gain as much knowledge as you can.

When a project gets stuck, draw more on your manager’s strength. Is the business side under a tight deadline? Is a partner uncooperative? Whenever higher-level communication is involved, report to your manager and let them help drive execution from a broader perspective. But before going to your manager, do not merely throw the problem at them; offer possible solutions and an expected timeline. That way, when it comes time to fight for resources or negotiate, your manager will not be so passive.

For business development, business knowledge is one of the foundations developers must master. When you encounter business problems, draw more on the business side’s strength. Ask them about the background, possible approaches, and reasons behind an issue. Communicating more with the business side not only helps you master more business knowledge, but, from a utilitarian perspective, also lets them get to know you. As everyone becomes more familiar, gaps in later collaboration shrink and work becomes smoother.

---

Borrowing arrows with a straw boat requires not only courage but also wisdom. Prepare the boat before talking, and pay attention to the time and setting. Expressing gratitude afterwards is indispensable too. Whether it is a simple “thanks,” a coffee, or a meal is up to you~~~

## Expectations and Project Management
Whether writing code or managing technical projects as a PM, the core is ensuring that things are delivered on time. There will always be things we do not understand along the way, so balancing unknown pitfalls and fixed delivery dates has been one of the most painful parts of being a technical PM since I joined.

If more than 30% of a project is unfamiliar to you, I recommend leaving yourself more buffer. There are two reasons. With unknown pitfalls, good luck may let you skip right over them; with bad luck, you may fall into one and be unable to get out for a week. No matter the project’s size, as its owner, we cannot let delivery time fluctuate with luck. That would leave us passive, affect the project’s external communication, and also affect frontline operations.

Leaving buffer is not only about giving yourself more time to encounter pitfalls; it also gives you more room to discuss schedules with the business side. If you begin by agreeing on a very tight deadline that can barely be met with overtime, the project will very likely be delayed. That will hurt your reputation with partners. Uncle Lu Xun once said: “Chinese people always like reconciliation and compromise. For example, if you say this room is too dark and a skylight must be opened, everyone will surely refuse; but if you advocate tearing off the roof, they will come to compromise and agree to open a window.” So if you estimate a schedule with buffer at the outset, you have plenty of room later to decide whether to tear off the roof or open a skylight.

But sometimes the schedule is not something small-P employees like us can decide. There are piles of projects that must go live before 9/30 or 3/30; every one is labeled P0 or the Nth growth curve and declared mandatory. There is no room for buffer. What should we do then?

Past experience tells me that throughout a project of continually discovering and resolving risks, any risk that is hard to solve must be synchronized with your manager. Let your manager understand the project’s progress in time and appropriately manage stakeholders’ expectations. That way, you will not give all the experts a SURPISE at every project milestone.

---

I remember writing a newcomer post about being a technical PM about half a year after joining. Interested readers are welcome to criticize it: [Lessons from My First Technical Project Management Role](https://wxxlamp.cn/en/2022/01/16/tech-pm-first/)

## Shared Joy Is Better Than Solitary Joy
<font style="color:rgb(51, 51, 51);">During my three years at Alibaba, I met many outstanding senior colleagues. Most of them gave me very important help during my time at Alibaba. When I asked why they would still make time to answer my questions despite being so busy, their answers were strikingly similar:</font>

<font style="color:rgb(51, 51, 51);">“Because I was once soaked by the rain myself, I know how painful these tedious things can be.”</font>

<font style="color:rgb(51, 51, 51);">“Once you understand these conceptual things, you take many fewer detours. There is no need for you to waste time on things with no value.”</font>

<font style="color:rgb(51, 51, 51);">I was deeply moved. To me, this is the best expression of Alibaba’s senior-junior culture. From my internship through campus recruitment, every senior colleague and manager I worked with did their best to help me land on my feet: teaching me technical principles, showing me how to learn and grow, how to manage projects, and how to control risks. I am grateful for every moment spent with them over these three years. Those days are among the most valuable treasures of my life (one of them, hahaha).</font>

<font style="color:rgb(51, 51, 51);">So if you have time, help new friends a little more. Before they have grown up, offer less PUA and more help within your ability. It makes you happy and everyone else happy, and little by little the team atmosphere improves and Alibaba’s culture is passed on.</font>

<font style="color:rgb(51, 51, 51);">And when we help them grow, is that not a form of growth for ourselves too?</font>

## Is Everything Worth Competing Over?
<font style="color:rgb(51, 51, 51);">I joined Alibaba as an intern in 2020 and was one of the lucky undergraduate students who converted to a full-time role through campus recruitment. Internet companies expanded campus hiring heavily in 2020, 2021, and 2022. From today’s perspective, under current hiring standards, there is no way an ordinary undergraduate like me would have been hired. Campus hires in my department now start with master’s degrees and have 985 universities as a baseline. In the competition over academic credentials, I had already lost at the starting line as a developer.</font>

<font style="color:rgb(51, 51, 51);">If I cannot compete on academic credentials, what else can I compete on? Overtime hours? Lines of code? Or logged hours in Aone?</font>

<font style="color:rgb(51, 51, 51);">I think all of these are process metrics. Competing over them may comfort or ease managers’ anxiety, but it is difficult for them to solve any other problem in a meaningful way, and they do nothing to help our own growth or improvement.</font>

<font style="color:rgb(51, 51, 51);">Top internet companies are reservoirs of talent, and excellent people are everywhere around us: technically capable, business-savvy, and often equipped with their own ways of dealing with people and situations. As newcomers to the workplace, we should work hard on our own skills, learn from the experts around us, improve technically, learn the business, and then put what we learn into practice. We should move from imitation to surpassing it and form a loop of learning, understanding, practice, and improvement.</font>

<font style="color:rgb(51, 51, 51);">After gaining foundational technical and business ability, business developers should not focus only on their own small technical domain. Gradually start competing on business understanding: learn the background, development, and plans of the business you build for, and practice considering problems from a broader view. Alibaba is still tolerant of newcomers making mistakes. Campus hires can experiment quickly, keep growing, wait for opportunities, and take on greater responsibility. I once came across a good talk by Zhang Yiming:</font>[张一鸣演讲整理 (in Chinese)](https://xueqiu.com/2684655177/154256082)

<font style="color:rgb(51, 51, 51);">Slow down a little. Give yourself some time to find one or two things you truly want to do in work and in life, then keep doing them. Do not compete over meaningless metrics. Campus hires: begin by competing with yourself.</font>

## You Hit a Pitfall—Then What?
As newcomers, when we first join there are always many things we do not understand. Some people may not even have used the development language commonly used in their department before. This is entirely normal. In the first year after joining, everyone falls into all kinds of pitfalls. I remember hitting many myself:

1. Batch calls from a DTS task triggered downstream alerts
2. An Aochuang deployment went live but did not take effect
3. Missing configuration for certain tenants caused an NPE, and so on

Some even caused P5 incidents. During the postmortems, my manager and senior colleagues helped me summarize the lessons, and I gained a great deal. Many people treat these as dark marks on their work record and do not want to face them. But for campus hires, the opposite is true: as long as the issue is not too serious, they are excellent chances to correct mistakes. As the saying goes, the best memory is worse than the palest ink. Like keeping a notebook of wrong answers in high school, record the pitfalls you have encountered. One day, when you encounter a similar problem for a second time, the scene of the first failure will suddenly come to mind. You can open the record, successfully avoid the pitfall, and keep moving forward.

People have a high tolerance for campus hires’ mistakes, so new colleagues must use this period to experiment and learn. When I was interning, a senior colleague gave me some suggestions during a code review, but I did not take them seriously and did not correct them. He sternly pointed out the problem with how I responded to comments and patiently taught me: “When someone helps you by pointing out mistakes in a CR, you must respond, discuss, or fix them. It shows that you value the reviewer. If you do not reply, it will be hard to get high-quality comments when you ask the same people for CR in the future.” That advice has served me well. After I formally joined, whenever a senior organized a broad CR and I received high-quality feedback, I would immediately submit a patch to fix it. The earlier a fix is made, the lower the risk of release.

At the same time, after hitting a pitfall, remember not only to avoid it yourself. If you can turn the lesson into public documentation or a knowledge base to keep others from hitting it, or fix the pitfall along the way, that is even more meritorious. (Of course, how to let others know you fixed it is an art //v//)

## Understand Clearly, Explain Clearly
<font style="color:rgb(51, 51, 51);">As programmers, we deal more with machines in day-to-day development, but communication with people is unavoidable in project management. Information entropy inevitably causes loss during transmission. So in communication, we need to use every possible way to make sure information is conveyed as correctly and completely as possible.</font>

<font style="color:rgb(51, 51, 51);">Communication is a skill that requires long-term practice. Two especially important points are patience and attentiveness. When listening, give your partner enough room to express themselves. Under normal circumstances, do not rush to deny or interrupt them—just as you would not want to be interrupted when speaking. What we need to do is listen carefully, note and digest the points the other person wants to express one by one. Before answering, we can also restate what the other person has just said in a few sentences to reduce the GAP between the two people as much as possible.</font>

<font style="color:rgb(51, 51, 51);">Likewise, when expressing your own views, try to organize them point by point. Like writing an essay, use a general-specific-general structure: state the key point at the beginning and end, with the middle explaining it in organized points. Also be sure to provide context and background. Otherwise, it is easy to confuse the recipient and create an awkward situation in which the two sides are talking past each other. This is especially true when consulting someone about a problem: if you ask only about one specific detail, they may find it hard to grasp the meaning immediately; if you explain the background clearly, communication may be much smoother.</font>

<font style="color:rgb(51, 51, 51);">But after all, every technique is only decoration. When your own influence is strong enough, many things resolve themselves.</font>

## Embrace Change
Embracing change is one of the New Six Veins, and no colleague is unfamiliar with it. At the company, embracing change is not merely a slogan; it is vividly reflected in action. Many people answer the organization’s call to “embrace change” every fiscal year, or even every half fiscal year, switching businesses, teams, and managers. Under organizational moves, they meet new people and take on new challenges.

As a campus hire, I initially did not feel the meaning of the word “change” very deeply. The first time I felt it was five months after I joined, when the whole group was notified that we would move to another BU. Since only the organizational relationship changed and the colleagues and manager I worked with did not, I had only an intuitive understanding of this change. The second time was in 2022, when the manager who had led me since my internship graduated from Alibaba and the entire team fell into a vortex. That time made me think. The third time was my own choice: choosing a different environment in which to continue working.

These changes left me with several thoughts:

First, many campus hires may have a misconception when they enter work: they think they must do something closely related to their major, study technology intensely, and write code. But after entering the workplace, I think this student mindset needs to shift slightly. Of course we should keep improving technically, but the core should be to focus on needs and organizational needs, and apply our technology or ability to those needs. The essence of an intermediary making money is matching supply and demand; sometimes making reports or thinking about the business is also growth.

Second, change has two sides. It means leaving your original comfort zone, but it also means facing a new environment and perhaps greater opportunities. After moving from one organization to another, discomfort and unfamiliarity are challenges we must face while first integrating. Some people may think when facing change, “Why change them instead of me?” Personally, I feel we should not assume too much malice from the organization. Perhaps we have not noticed that being moved from our original place may mean that our development there has already become constrained. So it is better to embrace this change with a more positive attitude and start again in a new field.

Third, a loss may turn out to be a blessing. Some changes may seem to cost us in the short term, but who can say what will happen in the long run? In only three years, I have seen many examples: changes that initially seemed good but later developed away from what people expected; and changes that began in utter disaster but later opened into a bright future. So when facing change, do your work well with a positive mindset, stay grounded while finding creative opportunities, and wait quietly for flowers to bloom.

We must acknowledge one fact: a business can keep running without any particular person. Most developers do not have technical ability so exceptional that it leaves everyone else in the dust. At first I naively thought, “This expert understands this technology so well—what will happen if their business changes?” After working longer, I gradually found that only when people change can things change. There is no requirement that cannot be solved by adding code, adding person-days, or doing a refactor. Though the so-called refactor may simply implement the previous feature again—you tell me, does it work or not? Hahaha.

The ability to learn is very important. When facing change, we must learn to integrate into a new environment quickly. Learn to understand the business quickly, take over unfamiliar code logic quickly, and develop your own methodology. Remember: we will never again have the happy time of a campus hire getting two full months just to familiarize ourselves with the code. The ability to deliver business requirements in unfamiliar code without creating risks, while even maintaining architectural consistency, is the foundational ability for a programmer to embrace change in the environment of our company.

In change, we must know this: no matter how the people and things around us change, the constant is always ourselves. Improving our abilities and cultivating ourselves through events is the enduring foundation amid change.

## High P and Low P
I have met many P9s at work. Their basic abilities are strong, and communicating with them feels like a spring breeze. But you cannot talk deeply with them for too long: before long, you find that many like to make sweeping pronouncements about fields they do not understand well. One HR person believed that graduate students from Tsinghua and Peking University in technical roles were inferior to master’s graduates from UCL and KCL; another sales leader made many basic factual mistakes while harshly reviewing DeepSeek. So as a campus hire, do not automatically put a flattering filter on high-P people. As the saying goes: “When you are out in the world, your identity is bestowed by the company.” It is hard to say how much real ability they have. At the very least, in the field you know best, they may truly know less than you.

What I also want to say is that many high-P people today rose during the internet boom years, and their knowledge base and learning ability may no longer keep pace with the times. Many campus hires still want to copy the old path: they arrive and want a promotion, imagining P6 in two years, P7 in two years, P8 in three years, and perhaps P9 after a lucky break. Frankly, the odds are small. No matter how hard you strive, the final result may still differ greatly from your expectations, because promotion is not only about ability; luck matters a great deal too. Here are a few external factors: whether you frequently change teams, whether you meet a good manager, whether there is an opening for promotion, whether the business is growing, whether your age is appropriate, and so on.

Although a soldier who does not want to become a general is not a good soldier, organizational problems arrive once a company grows large. You may even get caught in the crossfire for no reason because of senior management policies. So sometimes, even if you work very hard, you may not get the result you want. That is entirely normal. I have seen many people with very strong business and technical abilities who did not get promoted because of various factors. As the saying goes, a grain of ash from an era becomes a mountain when it falls on a person. Keep an even mindset, let go of titles, and treat every person at the company for who they are.

## Catch Rainwater and Repair the Roof
Although not everything is worth competing over, in today’s intensely competitive environment we often cannot avoid getting drawn into internal competition and numbly doing the same things over and over. The passion and courage we had when first entering work can gradually be worn away by an environment of constantly taking on passive requirements.

Sometimes, we may agonize every day over colleagues’ negative opinions; lose sleep over a small oversight at work; or become gloomy and shut ourselves off because a project is unfinished. “Hell is other people.” After working for a long time, we often fall into the evaluation system around us, becoming slaves to others’ words instead of masters of ourselves. At such times, seeking outward may be one solution.

The company’s halo and an individual’s ability are different things. Alongside internal company evaluation standards, try to use external evaluation to position yourself more accurately. In your free time, catch more rainwater and prepare for a rainy day; only then can you stay independent when the downpour comes. Looking back on the great layoffs of 2022 still makes my legs tremble with fear.

Preparing for a rainy day and repairing the roof while the weather is clear are equally necessary. When there are fewer requirements, relax physically but stay mentally alert. Learn more about competitors’ products and movements, and reflect on your strengths and weaknesses at work. Keep track of industry trends in your field, and feed them back into your business and technology. Build a more comprehensive evaluation system for yourself with a positive attitude, position yourself clearly, and improve accordingly. As an aside, large models are so popular now that every department hopes to use them to ease immediate problems, tell a new story, and paint a grand vision. If we ordinary soldiers do not understand these things and only keep doing curd, we may seem to be in a comfort zone but are actually pushing ourselves into an abyss. When an avalanche occurs, no snowflake is innocent.

---

The sea is wide enough for fish to leap; the sky is high enough for birds to fly.

Whatever happens, this is only a job. Becoming depressed because of work is simply not worth it. Cherish every friend around you, try to reconcile with yourself, accept what you cannot do, strive for what you can gain, face the results calmly, and be a friend to life.

When mountains and rivers seem to leave no road, beyond dark willows and bright flowers lies another village.

## A New Beginning
I originally wanted to publish this article on my third anniversary, but a series of events happened in between, and the delay stretched to half a year. Still, despite procrastinating for so long, I am glad it is finally published:)

It so happens that I will attend the company’s three-year anniversary event on February 17. “What is past cannot be undone; what lies ahead can still be pursued.” With this, I commemorate my third anniversary at Alibaba and welcome new challenges here ^_^
