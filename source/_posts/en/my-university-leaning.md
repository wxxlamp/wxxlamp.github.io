---
title: The Technical Knowledge System I Built at University
tags:
  - 学习方法
  - 计算机系统
  - 职业成长
categories:
  - 基础夯实
date: 2021-04-29 10:36
description: >-
  A four-year university knowledge review organized around professional,
  communication, and learning skills. It moves from hardware and operating
  systems through languages and business, emphasizes ownership, and advocates
  purposeful study, abstraction, and practice.
lang: en
translation_of: my-university-leaning
---

*I have not updated the blog for a while, chiefly because I have been preparing for a teaching-certificate interview while writing my graduation project and thesis. Today's article is adapted from the professional overview in my thesis, with minor changes and private professional information removed. It summarizes what I learned at university.*

From my perspective, the knowledge I gained at university falls into three parts: professional ability, communication ability, and learning ability. I will discuss each in turn.

### I. Professional Ability

Moving from the inside outward, I divide professional ability into hardware, operating systems, programming languages, programs, and business. “Inside outward” is only a loose description because we cannot objectively decide whether an operating system or programming language is more internal. This ordering better reflects how programmers encounter them.

*These modules describe only my own field and follow my personal understanding.*

#### 1. Hardware

Hardware includes CPUs, GPUs, memory, disks, forms of I/O such as network I/O, buses, motherboards, and more. Combined, these components form a physical server. Each manufacturer and architecture has distinct characteristics; CPU architectures, for example, include ARM and x86.

How do CPUs and GPUs differ? In my view, CPUs are suited to general computation and contain complex logic for branching and prediction. GPUs are suited to massively parallel computation. Structurally, CPUs have larger caches, while GPUs have more ALUs.

We often compare registers, memory, and disks by speed. Memory is far faster than disk, and registers are much faster than memory. Mechanical disks were slow because they depended on moving heads, while solid-state drives are now common. Because these levels differ in speed, much of what we call high performance consists of strategies that improve register utilization.

#### 2. Operating Systems

According to *Modern Operating Systems*, an OS has two purposes: abstract the machine for user programs so programmers can work conveniently, and manage computer resources so hardware is used efficiently. Modern operating systems are increasingly multicore, virtualized, and cloud-based. I know only the surface of Docker and Kubernetes, so I will leave those trends aside.

On PCs, operating-system families include System/360, Windows, and Unix. Linux, FreeBSD, and related systems descend from Bell Labs' Unix. Because most services now run on Linux and universities teach it, this section focuses on Linux.

Structurally, Linux can be viewed as Shell/GUI and kernel layers. Strictly speaking, shells and GUIs are not the operating system itself; they provide user interaction. User programs run in user mode, while the kernel isolates them from hardware. Any program accessing memory, hardware, or network resources must switch into kernel mode, preserving system security and stability.

By function, an OS chiefly provides process, memory, file, and I/O management. Resource management includes CPU scheduling of processes, threads, and coroutines. Memory management covers paging, segmentation, combined segmented paging, and virtual memory. I/O management includes network topics such as zero-copy, DMA, blocking versus nonblocking operation, and synchronous versus asynchronous operation.

Process and thread management should be understood historically. We say a process is the basic unit of resource management and a thread the basic unit of scheduling. A process abstracts a program, memory, and computing resources; each has data, text, and stack segments. Processes have running, blocked, and ready states. Blocking may result from I/O or locks, and a blocked process cannot run. Switching processes lets an OS create apparent parallelism. But a process contains the task's complete data and program segments, making switching expensive, while sharing address spaces, handles, signals, and other data between processes is cumbersome. Threads emerged in response. Thread switches can be ten to one hundred times faster, and threads access all data in their process. When one thread blocks on I/O, the OS can run another thread's computation. Yet threads do not solve everything: switching them still enters kernel mode, and frequent context switches waste CPU resources. If we implement user-space threads and switch tasks entirely in user mode, we can save that cost; this is the idea behind coroutines. Coroutines are no universal solution either. Blocking I/O suspends the whole thread and therefore every coroutine on it, and users must define coroutine scheduling, raising the entry barrier. Thread synchronization also requires understanding wake-up, `join`, `yield`, locking, and deadlock avoidance, with classic problems such as dining philosophers, sleeping barbers, and the banker algorithm.

Memory management abstracts storage through address spaces. Swapping and virtual memory even let disk serve as memory. Under virtual memory, the MMU maps program-generated virtual addresses to physical addresses using page tables. If an address is absent, a page fault swaps the required page in from disk. Translation lookaside buffers reduce repeated memory accesses caused by page tables, while multilevel page tables accelerate paging. Paging is a one-dimensional abstraction for storage; segmentation is a two-dimensional abstraction for users, reflected in data, program, and stack segments. The LRU page-replacement algorithm also appears frequently in engineering.

The storage-system abstraction is remarkably successful: it turns bits into files and folders ordinary users understand. Interaction between the OS and storage belongs broadly to I/O, though storage discussions usually focus on file systems.

Consider I/O through a web server using synchronous blocking operation. To read an input stream from a socket, a process first traps from user to kernel mode. The kernel **blocks** while listening until a network connection arrives, then instructs DMA to read NIC data into kernel memory. The OS can schedule other threads, but the current thread remains blocked. When DMA finishes, it interrupts the CPU. The OS reschedules the original thread and copies data from kernel to user space. The process returns to user mode, performs its business logic, and persists data to disk. Persistence again traps into kernel mode; the CPU copies user-space data into kernel space and asks DMA to write it to disk. DMA reduces wasted CPU work. If no business processing is required, kernel memory may be mapped with `mmap` to accelerate copying. What if another connection enters during blocking I/O? We must create another thread to accept it—the familiar BIO plus multithreading server model. Creating one thread for every connection does not scale and wastes memory. The OS therefore provides nonblocking I/O. During the two copies from NIC to user buffer, the user thread is not continuously blocked; it repeatedly asks whether data is ready. One thread can poll accepted connections and process those whose data is ready, producing `select`-based multiplexing. But `select` copies an accepted-descriptor array from user to kernel space and returns only the number of readable file descriptors. `epoll` instead communicates changed parts rather than the whole array and uses asynchronous event wake-ups, so the kernel returns only descriptors with I/O events. This greatly improves performance.

At the OS level, network communication also matters. Computer networks let machines worldwide connect through their operating systems. Two standard layer models exist: the seven-layer OSI model and four-layer TCP/IP model. Common protocols include IP at the network layer; TCP and UDP, with port numbers, at the transport layer; and HTTP, FTP, WebSocket, DNS, and SMTP at the application layer. Networking study emphasizes TCP's three-way handshake and four-way termination, which establish and close reliable connections despite network uncertainty, along with congestion control and flow control that regulate data volume between sender and receiver.

#### 3. Programming Languages

*Excluding assembly and machine language.*

Programming languages are tools; none is inherently good or bad. Whatever their syntax, they ultimately call operating-system APIs and cause the OS to read, store, compute, or communicate through hardware.

Languages may be object-oriented or procedural, static or dynamic, compiled or interpreted, and so forth. Differences in compilation, runtime, and use produce different strengths: JavaScript suits frontend development, the C family suits low-level and backend work, Java suits backend work, and Python suits crawlers. But suitability for one field never means confinement to it. Java can build backends, Swing clients, and applet or JSP pages.

Compare C with Java:

> A C programmer sees memory from the system's perspective—as a continuous byte array. A C program is at least one process and maps directly onto the OS process layout: program text and data, user stack, runtime heap, shared libraries, and inaccessible kernel virtual memory. `HelloWorld.c` code resides in the program-text region, static variables in the data region, function addresses and variables on the user stack, and `malloc` data on the runtime heap.
>
> Java's VM adds another abstraction, dividing memory into thread-private program counters, JVM stacks, and native method stacks, plus a shared heap and method area. Object instances reside on the heap; class information, methods, and static variables reside in the method area.
>
> C programmers access byte arrays, while Java programmers access abstract objects. C can reach lower levels and perform more operations, but access brings responsibility: without object-level abstraction, large C programs can suffer buffer overflows, out-of-bounds access, corrupt text, and other mysterious faults.
>
> C programmers allocate and release memory explicitly. Java's GC reclaims unreachable objects automatically, but causes stop-the-world pauses and makes reclamation timing unpredictable. C gives full control, yet forgetting to `free` memory can cause immeasurable damage.
>
> C provides complete control over memory. Java delegates memory operations through a VM abstraction. The VM prevents many severe bugs and makes Java easy to learn, but also produces developers of uneven skill, a frequent industry criticism.
>
> (Excerpted from https://wxxlamp.cn/en/2020/12/17/java-memory/ )

Every language requires fundamentals such as variables, branches, loops, pointers, and references. We must look through a language to its memory model and know the bit width of each variable type, along with facts such as 8 bits = 1 byte and 1 KB = 1,024 bytes, bitwise operations, complements, and base conversion. One curiosity: why does opening an ordinary compiled program as text reveal groups such as `cafe babe 0000 0037 0020 0a00 0400 180a`, arranged as two bytes or sixteen bits at a time? I still do not know.

#### 4. Programs

Above programming languages sit programs. People write many kinds of programs, which I roughly divide into:

1. Fundamental tools such as compilers, linkers, and VMs.
2. Middleware such as Redis, MySQL, Kubernetes, and Docker.
3. Frameworks such as Spring, LogicSvr, and JUnit.
4. Business applications for ordinary users, such as Taobao and WeChat.

We should understand development and iteration processes: requirement review, high-level design, detailed design with flowcharts, class diagrams, and patterns, coding, unit/canary/functional/end-to-end testing, system construction, and operations.

The most important abilities here are coding, bug fixing, and architecture. New graduates do not immediately design high-performance, highly available, extensible, consistent architectures. They begin as individual contributors implementing CRUD requirements inside existing frameworks. Good habits should produce code readable by both machines and people. Documentation and comments are equally important: they record iteration plans and direction, overall architecture, and the business model, and are essential in large systems.

Programming continually returns to computation and storage, representing time and space. Current theory and experience show that both cannot be minimized simultaneously. A system cannot be maximally fast while occupying minimal storage. Solutions exchange time for space or space for time; neither is inherently correct. Current hardware often permits using space to save time, as with multithreading, thread pools, and caches. In object-oriented classes, fields represent data structures and space, while methods represent algorithms and time. At runtime fields occupy memory and methods consume CPU computation.

Data structures and algorithms correspond to space and time. Heaps, stacks, queues, trees, graphs, arrays, and linked lists abstract memory for convenient programming. Fundamental algorithmic approaches include greedy methods, divide and conquer, dynamic programming, backtracking, and branch and bound, with applications such as sorting, Huffman trees, DFS, and BFS.

Beyond coding, we should master system design. I judge a design by four standards: performance, availability, efficiency, and security.

Performance is the computation and I/O load a system supports, measured through metrics such as TPS. Clustering, caching, asynchronous I/O, batching, pooling, multithreading, and optimistic locks can improve it. Every technique has costs: cache consistency, reliable asynchronous consumption, stateless clusters, thread safety, and context independence in pools all require solutions.

Availability is the time a system serves normally, often described as five nines or 99%. Multiple replicas, degradation, rate limiting, and timely circuit breaking improve it; Redis Sentinel uses replicas for availability. Replication also requires strong or BASE-style consistency. Paxos is a common algorithm, and WeChat has long used PaxosStore with good results.

Efficiency concerns business architecture and iteration. Many businesses need rapid experiments and releases. This requires suitable frameworks such as the Spring family, formal iteration processes such as agile development, and appropriate domain divisions such as DDD and microservices.

Security means protecting business logic and users. Systems must resist SQL injection, XSS, DDoS, CSRF, ARP spoofing, and other web attacks.

#### 5. Business

A good developer also understands the business.

Many computing professionals want highly technical, lightly domain-specific work, such as building caching, communication, pooling, or asynchronous middleware. It can develop technical skill, but few receive the opportunity because positions are scarce and the required expertise is high.

Understanding a business reveals its direction of evolution and enables architecture that improves development efficiency. Only then can engineers question requirements from product and operations colleagues and feed insight back into the business ecosystem to create commercial value.

Software engineers need business ability alongside technical ability. Financial-software developers must understand finance; developers in traditional industries must understand their domains. Nearly every job description I have seen says that relevant industry experience is preferred, demonstrating its importance.

### II. Communication Ability

Communication is necessary with friends, classmates, teachers, colleagues, and managers. Communicating with teachers provides knowledge; with classmates, adaptation; with friends, self-improvement.

At work, communication with product managers aligns goals, communication with developers coordinates schedules, and communication with managers synchronizes projects. Failure with product can cause rework, longer development, and delayed launch. Failure with developers can desynchronize progress and introduce defects. Failure with a manager can misalign goals and indirectly damage year-end performance.

Communication requires initiative. Initiative means ownership and responsibility: truly take responsibility for a project, proactively push and follow up, and understand it completely.

More broadly, we must communicate with society and our environment to obtain needed information, break information barriers, and improve ourselves. Communication is not merely speaking but interpersonal ability. It may be less concrete than professional knowledge, but after entering the workplace it can become decisive.

### III. Learning Ability

Learning ability is not cramming or rote memorization, but a cyclical and progressively deepening process. I divide it into learning, understanding, and application.

Learning needs motivation and demand. Interest creates curiosity and self-direction, leading a student to absorb and think actively. During study, summarize and discover how new knowledge differs from existing knowledge. This deepens understanding and builds the ability to transfer insight. Knowledge must then be tested and applied elsewhere to create value; only then is the learning cycle complete.

Many people read source code such as Spring or MyBatis but forget it immediately and feel they gained nothing. They merely read, skip what they do not understand, and finish with only a vague impression. The missing element is method. First know why you are reading. I studied MyBatis source because I faced a mapping requirement and wanted to understand its implementation. A purpose supplies motivation: learn with a question. Afterward, summarize and abstract both the solution and other strong ideas. Finally, write a demo and apply the knowledge to solve a real problem.

### IV. Afterword

The more we know, the more we realize how little we know. This record represents my overall understanding of computing and may contain problems; corrections are welcome.

The road ahead is long and difficult; I will search high and low.
