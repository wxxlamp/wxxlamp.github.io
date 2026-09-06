---
title: Understanding Zero-Copy I/O
tags:
  - 计算机系统
  - 网络通信
  - 性能优化
categories:
  - 基础夯实
date: 2023-02-07 10:36
description: >-
  A systematic explanation of zero-copy I/O, beginning with the four-copy
  overhead of ordinary I/O and covering DMA, mmap, sendfile, and Direct I/O,
  including their use cases and limitations.
lang: en
translation_of: zero-copy
---

As a web developer, network I/O is unavoidable, and zero-copy is an important part of it. After repeatedly reading scattered articles, I decided to summarize it here.

Understanding zero-copy starts with the operating system's I/O flow. Because user mode and kernel mode are separated for safety and caching, ordinary reads and writes work as follows. A Java program adds another copy between off-heap and heap memory.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/62c75fdf_zero-copy-1.png" align="middle"/>

1. A user's `read` invokes a system call and enters kernel mode. DMA copies data from disk into the kernel buffer.
2. When DMA finishes, it interrupts the CPU. The CPU then copies the kernel-buffer data into user space.
3. The kernel wakes the relevant thread and returns the user-space data to it.
4. The user-space thread processes the data.
5. When the server responds, another system call asks the kernel to copy the data from user space into kernel space.
6. A network adapter uses DMA to copy the kernel-buffer data to the NIC, after which control returns to user mode.
7. The NIC sends the data.

Ignoring copies within user space and between physical devices and their drivers, this involves four data copies and four process-context switches. Zero-copy techniques reduce either the number of copies or the number of copies performed by the CPU under particular conditions. Common approaches include `mmap`, `sendfile`, DMA, and Direct I/O.

## DMA

In a conventional I/O flow, the CPU participates both when copying between physical devices, such as disk to memory, and between memory regions, such as user space to kernel space.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c1ddf61b_zero-copy-2.png" align="middle"/>

For large files, these unproductive copies waste substantial CPU capacity, which led to DMA. DMA stands for Direct Memory Access. It copies data directly from an I/O device into the kernel buffer. The CPU only sends DMA the copy instruction and does not perform the transfer itself, improving processor utilization.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/4e075fcb_zero-copy-3.png" align="middle"/>

mmap

Ordinary `read` plus `write` requires at least four copies, including the copy from kernel to user space for isolation and caching. If safety can be guaranteed, user and kernel space can share a buffer. That is what `mmap` provides.

`mmap`, or memory mapping, maps kernel and user memory together and avoids copying between them. A process can use pointers to read and write that memory, while the system writes dirty pages back to the corresponding file automatically, without further `read` or `write` calls. Kernel changes to the region are also reflected directly in user space, enabling file sharing between processes. Its signature is:

```basic
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
```

`mmap` generally replaces `read`:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/df1e9b25_zero-copy-4.png" align="middle"/>

With `mmap` plus `write`, I/O requires three memory copies, though still four context switches. `mmap` uses lazy loading based on page faults. Requesting 1,000 GB through `mmap` might consume only 100 MB of virtual address space—or allocate no physical memory at all—until access triggers page-fault allocation.

**However, `mmap` is not a silver bullet:**

1. The mapping size must be specified in advance, so `mmap` is unsuitable for files whose length changes.
2. The OS automatically writes dirty pages back to disk. With many random writes, `mmap` may be no faster than ordinary buffered writes.
3. `mmap` needs a contiguous virtual-address range. A 32-bit OS may expose only 2 GB of virtual memory, making it difficult to map an entire 4 GB file. It is therefore unsuitable for extremely large files.

## sendfile

If data is merely transferred without processing—for example, sending static HTML and JavaScript files to a browser—performing all those copies and context switches is excessive. `sendfile` transfers the file without user-space intervention:

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b057b8b7_zero-copy-5.png" align="middle"/>

This reduces data copies to three and context switches to two. One question remains: why must the kernel copy twice, from page cache to socket cache? That step can also be removed.

### sendfile + DMA Scatter/Gather

DMA scatter/gather was introduced in Linux 2.4. It records descriptors from the page cache—memory addresses and offsets—in the socket cache, then DMA uses them to copy data from the read buffer to the NIC. Compared with earlier versions, it removes one CPU copy.

<img src="https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/ebcf03bd_zero-copy-6.png" align="middle"/>

## Direct I/O

While `mmap` reduces copies by sharing a memory region between user and kernel space, Direct I/O lets hardware data bypass kernel-space buffers and enter user-space memory directly. User space interacts directly with the device, and writes go straight to disk rather than waiting for the operating system to flush them.

This reduces copies and speeds reads, but the application must assume responsibility for caching and related management. MySQL, for example, uses Direct I/O and maintains its own cache system. Although Direct I/O writes file data directly to disk, file metadata must still be flushed through the kernel using `fsync`.
