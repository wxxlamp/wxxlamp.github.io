---
title: Xingxing Wang - Resume
layout: resume-en
date: 2024-01-01
password: dynamic
name: Xingxing Wang
contact:
  phone: "17179887126"
  email: "wxxlamp@foxmail.com"
  birth: "Jan 2000"
  website: "https://wxxlamp.cn"
education:
  - school: Hong Kong University of Science and Technology (QS Top 50)
    major: Information Technology · Master's (Full-time)
    date: Sep 2024 – Oct 2025
    description: Outstanding academic performance, GPA 4.1/4.3. Courses include Blockchain, NLP, LLM, etc. Received Top Student Award Scholarship in Semester 24.
  - school: Zhengzhou University (Double First-Class / 211)
    major: Software Engineering · Bachelor's
    date: Sep 2017 – Jun 2021
    description: Outstanding academic performance, GPA 3.6/4.0 (Top 11 in major). Received National Encouragement Scholarship, recognized as "Three-Good Student" multiple times.
experience:
  - company: Alibaba - Alibaba.com Technology Department
    title: Senior Software Engineer (P6)
    date: Jul 2021 – Present
    description: Led design and development of Alibaba International's Global Seller business (merchant onboarding, settlement & AI). Previously responsible for credit guarantee development and limit migration; overall technical planning and iteration for financial insurance (OA credit sales, worry-free returns); built a zero-frontend operations platform from scratch. Performance rating of 3.75/3.5+ in over 60% of cycles.
projects:
  - name: Global Seller · Merchant Settlement Technical Lead
    date: Aug 2024 – Present
    summary: To address potential risks for Chinese merchants in cross-border trade and expand platform supply, Alibaba International supports global merchant onboarding and transaction fulfillment (Global Seller). Currently serves 15 country sites (SEA, North America, Europe, etc.), 5,000+ registered merchants, and cumulative withdrawals of tens of millions of USD.
    highlights:
      - "【Full Chain】Based on existing capabilities of the main platform (Chinese merchants), independently built the full-chain: merchant onboarding, transactions, guarantees, payments, settlements, and gateway for each overseas country with tenant customization. Led the full-chain launch of Japan site as Technical Lead;"
      - "【Access & Withdrawal】Built global merchant access and withdrawal capabilities with unified access, asset, and withdrawal workflows. Leveraging iPay, Yeepay, Standard Chartered and other fund channels, built channel routing, orchestration, and status management to support KYC, fund transfer, and withdrawal for multi-country merchants;"
      - "【Tenant Architecture】Led multi-tenant architecture upgrade for the supply chain merchant side via unified traffic entry, independent modules/apps, tenant log monitoring, tenant thread cache, and tenant config files. Resolved R&D efficiency (50% improvement for new sites), monitoring noise, and tenant isolation issues across countries;"
      - "【LLM】Built an LLM task platform from scratch, drove adoption of orchestrated LLMs (RAG, MCP) for OCR in KYC workflows and daily tech operations. Lowered merchant onboarding barriers and improved operational efficiency;"
      - "【Team Management】Managed technical planning for merchant and withdrawal domains (dotted-line lead of 3). Led development standards and code review guidelines. As Mentor, coached 2 social-recruited P6 engineers through probation."
  - name: Credit Limit System Refactoring · Technical Migration Lead
    date: Oct 2023 – Jul 2024
    summary: Alibaba International allocates advance repayment limits to merchants so they receive full payment after shipping. The limit system (online since 2016) was near collapse—spanning 3 data sources and 2 systems—with poor extensibility and severe data inconsistency. Led the overall splitting and reconstruction of tens-of-millions of records under strict constraints of 30+ TPS and zero financial errors.
    highlights:
      - "【Migration Strategy】Designed a smooth migration plan: full replay → incremental Binlog catch-up → dual-write verification → read traffic gray cut. Used step-size ID isolation and async dual-write to ensure zero-downtime, zero-impact migration;"
      - "【Migration Monitoring】Monitored dual-write accuracy via real-time log monitoring and near-real-time/real-time data reconciliation, promptly identifying and fixing concurrency and timezone issues;"
      - "【Performance Optimization】Optimized the 8-year-old credit page P90 from 10s to 1s via concurrent downstream calls, invalid-call reduction, multi-level caching, and business logic optimization. Post-migration interface latency improved from 1s to 20ms;"
      - "【R&D Efficiency】Refactored the credit domain model with computation/storage separation and configurable limit types (scenario + tenant). New limit development time reduced from 20 to 4 person-days;"
      - "【Availability】Ensured credit limit data consistency via optimistic locking and buyer-seller limit deduction consistency via TCC."
  - name: Guarantee Insurance Business · Technical PM & Core Developer
    date: Jul 2021 – Sep 2023
    summary: To improve Alibaba International's transaction certainty and merchant fund/goods security, introduced third-party insurers to cover chargebacks, returns, and tail payments. Currently serves 60,000+ buyers/sellers, with 10,000+ daily policies and 1,000+ QPS. Responsible for project management and architecture design.
    highlights:
      - "【Credit Platform】Built an insurance credit platform from scratch: process engine for node orchestration and retry; SPI + strategy pattern for multi-product credit extension; domain events for state transitions; local transaction tables + monitoring reconciliation for eventual consistency;"
      - "【Multi-region Deployment】Built three data centers (China, US, Singapore) to meet overseas compliance requirements, with bidirectional data sync, step-size mechanism to avoid data overwriting, and buyer-dimension traffic routing for read-write consistency;"
      - "【Quality Building】Established unit and integration test frameworks, ensuring 60% incremental coverage per release, reducing joint-debugging, testing, and refactoring costs;"
      - "【Performance Optimization】As Financial Domain Promotion PM, led stress testing. Scaled app QPS from 600 to 5,000 via additional machines, multi-level caching, and multi-threaded queries;"
      - "【Operations Platform】Built a server-driven UI system (layout, actions, permissions) that dynamically renders frontend pages at runtime with zero frontend code, improving development efficiency by 50% (approved as a group innovation proposal)."
skills:
  - Familiar with LLM and Agent; experienced in SFT and Inference via LlamaFactory and HuggingFace; proficient in AI Coding;
  - Proficient in Java, multithreading; familiar with JVM, OS, MySQL, networking, algorithms and data structures; experienced in Java ecosystem (Spring, MyBatis) development;
  - Understands DDD and TDD; familiar with common design patterns, process engines, and mainstream microservice architectures and middleware (Redis, MetaQ, etc.);
  - Proficient in cross-border transaction and fund settlement full chain; strong self-learner, enjoys writing and summarizing; capable of mentoring new engineers and PM-ing medium-to-large technical projects (100+ person-days).
---
