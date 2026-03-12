---
title: Wang Xingxing - Resume
layout: resume-en
date: 2024-01-01
password: dynamic
name: Wang Xingxing
contact:
  phone: "+86 17179887126"
  email: "wxxlamp@foxmail.com"
  birth: "Jan 2000"
  website: "https://wxxlamp.cn"
education:
  - school: The Hong Kong University of Science and Technology (QS Ranking 50)
    major: Master of Science in Information Technology (Full-time)
    date: Sep 2024 – Oct 2025
    description: "Achieved an outstanding academic performance with GPA 4.1/4.3. Coursework includes Blockchain, NLP, LLM, etc. Awarded the \"Top Student Award Scholarship\" for the 2024 semester."
  - school: Zhengzhou University (Double First-Class / Project 211)
    major: Bachelor of Engineering in Software Engineering
    date: Sep 2017 – Jun 2021
    description: "Excelled academically with GPA 3.6/4.0 (Ranked 11th in major). Recipient of the National Encouragement Scholarship and repeatedly recognized as \"Merit Student\" of Zhengzhou University."
experience:
  - company: Alibaba Group - Alibaba.com Technology Department
    title: Senior Development Engineer (P6)
    date: Jul 2021 – Present
    description: "Led the design and development of the Global Seller Business (Transactions & Capital) on Alibaba International Station; Responsible for the development of Credit Guarantee Business and quota migration; Oversaw the overall technical planning and iterative development of Financial Insurance Business (OA, Free Return); Built an operation platform from scratch that requires no front-end development. Achieved a performance rating of GOOD in over 60% of review cycles."
projects:
  - name: Global Trade · Technical Lead of Merchant Settlement
    date: Aug 2024 – Present
    summary: "To mitigate potential risks in Chinese merchants' foreign trade operations and expand the platform's differentiated supply, Alibaba.com supports global merchants to onboard and fulfill transactions (Global Trade). Currently covering 15 country sites (Southeast Asia, North America, Europe, etc.), with over 5,000 onboarded merchants and cumulative withdrawal amount exceeding 10 million US dollars."
    highlights:
      - "【LLM Application】Responsible for LLM application in Global Trade scenarios, building an LLM task platform from scratch, and driving the adoption of LLMs (based on RAG, MCP) for OCR in KYC processes and daily technical operations. Reduced merchant onboarding barriers and improved business operational efficiency;"
      - "【Full Lifecycle】Based on the existing infrastructure for Chinese merchants, independently delivered end-to-end development and tenant customization for overseas merchant onboarding, transactions, assurance, payment, settlement, and gateway. As the technical lead, responsible for the full-lifecycle launch of the Japan site project;"
      - "【Onboarding & Withdrawal】Responsible for building global merchant onboarding and withdrawal capabilities, and establishing unified onboarding, asset, and withdrawal processes. Based on the underlying integration with multiple payment channels (iPay, Yeepay, Standard Chartered, etc.), built channel routing, orchestration, and status management capabilities to support KYC, fund allocation, and withdrawal needs of merchants across multiple countries;"
      - "【Multi-Tenant Architecture】Led the multi-tenant architecture upgrade for supply chain merchants, implementing tenant-level optimization through unified traffic entry/views, independent modules/applications, tenant-specific log monitoring, thread caching, and configuration files. Resolved R&D efficiency issues (50% improvement for new site onboarding), monitoring noise, and tenant isolation problems caused by cross-country tenant differences;"
      - "【Team Management】Responsible for technical planning and management of merchant and withdrawal domains (dotted-line Lead of 3 team members). Led the formulation of development standards and code review criteria for transaction merchant systems; Successfully mentored 2 external hires to P6 level and completion of probation as a Mentor."
  - name: Assurance Quota System Reconstruction · Technical Migration Lead
    date: Oct 2023 – Jul 2024
    summary: "Alibaba.com allocates advance payment quotas to onboarded merchants, enabling them to receive full payment upon delivery. The quota system (launched in 2016) had severely deteriorated, with data scattered across 3 data sources and 2 systems, suffering from poor scalability and critical data inconsistency. Responsible for leading the full split of 10-million-level data and reconstruction of the new system under strict constraints of 30+ TPS and zero financial errors."
    highlights:
      - "【Migration Strategy】Led the design of a seamless migration plan: \"full data replay, incremental Binlog synchronization, dual-write verification, gray-scale read traffic switch\". Utilized mechanisms such as step ID for new/old data isolation and asynchronous dual-write to ensure zero downtime and business transparency during migration;"
      - "【Migration Monitoring】Monitored the accuracy of dual-write traffic through real-time log monitoring and near-real-time data reconciliation, promptly identifying and fixing multiple dual-write issues including concurrency and time zone discrepancies;"
      - "【Performance Optimization】Optimized the 8-year-old quota page performance (90th percentile response time reduced from 10s to 1s) by concurrently orchestrating downstream credit/quota APIs, reducing invalid calls, implementing multi-level caching, and optimizing business logic. Interface latency improved from 1s to 20ms post-migration;"
      - "【R&D Efficiency】Reconstructed the quota domain model (separating computation and storage) and implemented configuration-driven (scenario + tenant) expansion for new quota types, reducing development effort for new quotas from 20 person-days to 4 person-days;"
      - "【System Availability】Ensured consistent update of quota data via optimistic locking, and consistency of buyer/seller quota deduction via TCC pattern."
  - name: Trade Insurance Business · Technical PM & Core Developer
    date: Jul 2021 – Sep 2023
    summary: "To enhance transaction certainty and protect merchants' capital/goods safety on the International Station, third-party insurance institutions were integrated to cover chargebacks, returns, and final payments. Currently serving over 60,000 buyers/sellers, with daily policy volume exceeding 10,000 and QPS over 1,000. Responsible for project management and architecture design of the Trade Insurance Business."
    highlights:
      - "【Credit Platform】Built an insurance credit platform from scratch through the OA Trade Credit project; Introduced workflow engine for node orchestration and retry; Adopted SPI mechanism combined with strategy pattern for credit scalability of different insurance products; Drove credit process and status flow via domain events to ensure efficient business delivery; Ensured eventual consistency in microservices through local transaction tables and monitoring reconciliation;"
      - "【Multi-Region Deployment】To comply with cross-border data regulatory requirements, deployed the insurance domain to new data centers in China, US, and Singapore for overseas architecture; Implemented bidirectional data synchronization, avoided data overwriting via step mechanism, and ensured read-write consistency through buyer-based traffic routing;"
      - "【Quality Assurance】Established and maintained unit/integration testing frameworks for related applications, ensuring 60% incremental code coverage for each release, reducing integration, testing, and refactoring costs;"
      - "【Performance Optimization】As the financial domain PM for peak promotions, led stress testing of the financial domain. Increased application QPS from 600 to 5,000 by scaling server capacity, implementing multi-level caching, and using multi-threaded queries;"
      - "【Operation Platform】Implemented server-side configuration-driven dynamic rendering of front-end pages (layout, operations, permissions, etc.) at runtime, eliminating the need for front-end development and improving development efficiency by 50% (approved as Group Innovation Proposal)."
skills:
  - "Familiar with LLM and Agent technologies, with hands-on experience in SFT and Inference based on LlamaFactory and HuggingFace; proficient in AI Coding;"
  - "Proficient in Java syntax and multi-threading; Knowledgeable in JVM, operating systems, MySQL databases, computer networks, common algorithms, and data structures; Mastered R&D processes based on Java ecosystem (Spring, MyBatis frameworks);"
  - "Understand DDD and TDD concepts, and familiar with common design patterns; Knowledgeable in workflow engines, common microservice architectures/components, and middleware such as Redis and MetaQ;"
  - "Proficient in the full lifecycle of cross-border transactions and fund settlement; Strong learning agility, passion for writing and summarization; Capable of mentoring new hires and managing medium-to-large technical projects (100+ person-days)."
---
