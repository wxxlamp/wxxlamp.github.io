---
title: Lessons from My First Technical Project Management Role
tags:
  - 技术管理
  - 职业成长
categories:
  - 采坑记录
date: 2022-01-16 10:36
description: >-
  A retrospective on leading a major project as a technical PM for the first
  time. It describes the four core responsibilities of a technical PM,
  requirement and project milestone processes, and more than ten practical
  lessons and project-management principles.
lang: en
translation_of: tech-pm-first
---

# Preface

After joining a new company through campus recruitment, I was a technical PM for the first time, approaching a 150-person-day major project end-to-end and from every perspective. I have many thoughts, so I am writing this retrospective. The ultimate responsibility of a technical PM is to ensure that a project launches on time, with quality and in full. After refining the responsibilities and breaking down the work, the following areas should be owned:

1. Communicate information: serve as the bridge between business (operations/product) and technology.
1. Handle miscellaneous work: address development work at boundaries and other shared affairs.
1. Coordinate solutions: determine interaction solutions for each domain and coordinate the overall technical flow.
1. Break down tasks: split business domains into technical domains and assign them to developers.

# Methods

To be a qualified technical PM, I summarized the following methods to help complete project-management work.
### Stakeholder map

1. Identify relationships: contacts for every domain, including testing, development, and front-end contacts. Strive to have project-team members know the interface owner for every domain before development truly begins.

### Project schedule

1. Use project-management tools properly: use Teambition/Project to schedule work, especially milestones and every person’s schedule. If a task cannot finish on time, communicate and warn promptly, then produce a solution.
1. Reserve BUFFER: surprises always happen, such as project-environment conflicts and leave. Tight first, loose later.
1. Arrange time points: determine every date and milestone, then synchronize them with stakeholders (business/PMO).

### Communicate constantly

1. Stand-ups: when uncertain risks and open issues arise, promptly hold a stand-up with the relevant people for synchronization and progress tracking. Escalate when needed and seek a manager’s help.
1. Weekly reports (progress and risk): report overall project progress and escalate project risks.

# Milestones

The work is broadly divided into requirements and projects. Their core process is the same, though there are differences. Requirement milestones apply to small development requirements staffed within a BU; project milestones apply to cross-BU development projects.
### Requirement milestones

1. PRD review (product/development/testing): functional flow.
2. Technical scheduling: development & self-test / integration / testing.
1. Technical review (PD/development/testing): from inside out, then outside in.
   1. Internal technical review: review flows/databases/monitoring.
   1. External technical review: review interactions (synchronous/asynchronous/idempotency/retry/exceptions).
   1. Internal re-review: review second-party libraries (they relate to interactions, so this follows interaction review).
   
   <img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/afce085d_tech-pm-first-1.jpeg" align="middle"/>
   
4. Development & self-test: development/UT/integration testing/API self-test/MOCK downstream.
5. Integration: first local integration with MOCK, then complete integration in the real environment.
6. CR (Owner/development): after integration, conduct CR, mainly checking whether code is wrong and whether internal logic can be optimized.
7. Test review/testing: for small requirements, no test review is needed; testing can directly follow the PRD.
8. Release: before release, determine release order and dependencies, as well as applications and configuration to release.
9. Canary: usually controlled from the front end. First run through production normally with test users, then gradually increase traffic and begin the canary.
4. Monitoring: after release, observe log alerts, offline tables and near-real-time data, status-flow monitoring, and so forth.

### Project milestones

1. BRD review: review the business-requirement document and understand business requirements.
2. Confirm resources: confirm technical resources; if insufficient, coordinate with the responsible people.
3. PRD review: review functional flows and understand product requirements.
4. Technical scheduling: schedule development, integration, and testing, and provide an approximate launch date.
1. Technical review: from inside out, then outside in.
   1. Internal technical review: state advancement/process flow.
   1. External technical review: interaction solution/integration conventions.
      1. Upstream technical review: determine fields required by upstream.
      1. Downstream technical review: request fields from downstream.
   3. Internal second-party-library review: interaction review.
   
   <img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b15eeaad_tech-pm-first-2.jpeg" align="middle"/>
   
6. Development self-test: development/UT/integration testing/API self-test/MOCK downstream.
7. Internal integration: integrate thoroughly internally. Once done, later APIs can safely MOCK, and integration with upstream is more reliable. Record every integration case.
8. External integration: first integrate locally and MOCK other areas; connect everything for complete integration last, reducing resource dependency.
9. Test review: at this point, ensure every case is included.
10. CodeReview: before CR, merge the main branch.
11. Smoke testing: run the full process through testing without MOCK.
12. Feature rehearsal: walk the entire feature through with business and product.
13. Reconciliation monitoring: complete these monitoring strategies.
    1. Data reconciliation: whether records exist, states match, amounts match, fees are deducted, and so on.
    1. Log monitoring: exception and error logs, plus business-total dashboards.
14. Release review
       1. Release order: note release start and end times, and dependencies between domains.
       2. Release applications: applications, second-party libraries, databases, offline tables, scheduled jobs, configuration, and so on.
       3. Canary plan: front-end canary, upstream canary, traffic proportions, and other plans.
15. Release in order: second-party libraries and downstream first.
16. Alert monitoring: repeatedly validate SLS logs and database content, including existing and new business.

# Lessons learned

1. Other collaborators’ technical schedules were uncertain, so development progress could not be driven **=>** If a TODO has no conclusion, leave an action and a time.
1. One API’s retry mechanism was undecided and only discovered before release **=>** The technical review must determine the interaction solution (synchronous/asynchronous/idempotency/retry/exceptions).
1. On taking over a new project, knowing the members is most important **=>** Use Xmind properly, for self-test and integration cases and every person’s contacts.
1. When integrating with collaborators, even if they modify locally, they called our environment. This meant we had to keep the project environment available constantly, which was unreasonable. We should MOCK first and integrate at an agreed time **=>** Before integration, agree on the integration plan, such as how to MOCK downstream and which real integration environment downstream can provide.
1. Because I initially did not understand one process well, I paid little attention to its test cases. A few days before launch, I still did not know whether some cases had passed, which affected my mood greatly **=>** PMs should go through every domain’s cases with testing where possible, list them, and have relevant people pass self-tests, so the self-test stage is under control.
1. If a solution is uncertain, promptly bring product and business together to check it (although everyone may be busy).
1. During technical review, a technical conflict in a domain involving a collaborator prevented progress **=>** When a milestone blocker blocks the whole project, do two things: arrange other parallel tasks, and warn and report to the manager.
1. During integration and testing, check every field and state on every order **=>** Before release, the insurer said one image had been transcoded twice. This should have been found during testing but remained until just before release.
1. A problem was found on the last testing day and needed modification, but release was the next day, leaving no time to fix and deploy **=>** Reserve at least two days of BUFFER after the test schedule.
1. In the second-phase release review, release began on the 6th and completed on the 7th, but only the 6th was marked **=>** When scheduling, provide both release start and end times.

# Conclusion

I had long talked about lacking the chance to touch the full product-development and iteration process; unexpectedly, the chance arrived so quickly. During the project’s first two weeks, I knew neither the business nor the technology. Whenever business asked about technology I was completely confused; when technology asked about business, I knew nothing either. Sometimes I even dreamed that I had ruined the project, and the pressure was indeed high.

But as the project progressed, I stepped into pit after pit and, with everyone pushing together, brought this several-hundred-person-day project online.

I felt that after stepping into so many pitfalls, I could not write nothing. So I left behind this journey of my thoughts and lessons learned as the first post of my PM career.
