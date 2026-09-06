---
title: Understanding Bitcoin and Blockchain from First Principles
tags:
  - 区块链
categories:
  - 基础夯实
date: 2025-09-07 10:36
description: >-
  A systematic introduction to the core principles of blockchain and Bitcoin,
  beginning with centralized and decentralized money and covering blockchain
  structure, hash pointers, asymmetric cryptography, UTXO, Proof of Work, and
  the complete lifecycle of a Bitcoin transaction.
lang: en
translation_of: what-is-bitcion-and-blockchain
---



Written for both technical readers and complete beginners, this article moves from decentralization and blockchain to the principles behind Bitcoin. Through explanations and questions, it aims to help everyone understand the essence and technical foundations of decentralized money.

# Centralization and Decentralization
Conceptually, centralization and decentralization represent two ways of storing data and executing logic. With centralization, data such as asset records is stored in one place or institution, and logic such as transactions is executed independently by a single system. With decentralization, also called a distributed model, data such as asset information is stored across multiple peer nodes, and logic such as transactions is valid only when recognized by all nodes.

## Advantages and Disadvantages of Centralized Money
Before blockchain appeared, almost every system was centralized. Note that distributed systems did exist, but they were generally controlled by a single organization and could not be extended freely to any organization or individual. A distributed database such as OceanBase is therefore still centralized.

A typical centralized application is centralized money. Backed by national credit, it is issued by each country's central bank as a measure of wealth and a medium of exchange, and it has unlimited legal tender status. Centralized money has two advantages:

1. **Stability**. Take the US dollar issued by the Federal Reserve as an example. The Fed regulates its value, making that value relatively stable and preventing **large fluctuations**. When people transact in dollars, the value of goods remains within a stable range. Centralized money is also backed by national credit: as long as the country remains stable, its currency can circulate.
2. **Risk resistance**. If money is stolen through an accidental or fraudulent transaction, centralized money backed by national credit can help users recover the lost amount through tracing, recovery proceedings, and other means.

Centralization has a major weakness, however: it is vulnerable to a single point of failure. If the central bank at that single point collapses, the centralized money supported by its national credit becomes water without a source. Holders' money may be reduced directly to zero, and the wealth it represents disappears as well. Centralized money also has the following disadvantages:

1. **Single-point control**. Because money is controlled by a centralized central bank, the money people hold can potentially be **frozen by that central bank** at any time. After the United States sanctioned Russia, for example, US dollars held by Russian companies in the United States and affiliated countries were frozen indefinitely without justification.
2. **Loss of central-bank credibility**. A central bank independently decides how much money to issue. If it is incompetent and makes a bad decision that results in **overissuance**, the ensuing inflation can drastically erode people's wealth. The now-abandoned Zimbabwean dollar, for example, ceased to function as money because of overissuance.
3. **Poor privacy**. When centralized money is used for transactions, every payment record except small cash transactions is recorded by the central bank. This means payment data that users consider private is visible to centralized institutions. If you buy a steamed bun through Alipay in the morning, for example, the central bank can associate that transaction with your ID whenever it wishes.
4. **Low cross-border efficiency**. Centralized money is especially inefficient in cross-border transactions conducted through the SWIFT system. Different countries have different central banks, each issuing its own currency. When centralized currencies issued by different entities are exchanged, settlement passes through multiple multinational banks. More participants make cross-border remittances extremely slow and expensive.

## Opportunities and Challenges of Decentralized Money
In countries whose governments enjoy very high public trust, centralized money meets the needs of 99% of people. But there will always be another 1% who are dissatisfied with the status quo and hope to address its flaws through decentralization.

With decentralized money, issuance and transactions are not dictated by one entity; they are decided collectively by all nodes that use the currency. There is no central bank, yet everyone is a central bank. If issuance and transactions require approval from a majority of community nodes, at least the following problems are addressed:

1. The currency can operate on nodes around the world. The failure of any single node does not affect its basic operation.
2. Issuance is no longer controlled by one institution or organization, reducing the risk that a single party will issue money recklessly. The amount issued must be approved by a majority of community nodes, and everyone has the right to participate.
3. Transactions are no longer controlled by one institution. Without agreement from a majority of community nodes, no transaction can be rejected or frozen.
4. Transactions run on nodes around the world. Domestic and international transactions are fundamentally the same, so cross-border payments can be more efficient than the current SWIFT system. Note that centralized money remains more efficient for domestic payments.

Judging from these problems, decentralized monetary transactions may seem far too “free” for most people. No sovereign state can accept a currency it cannot control through its central bank. An inability to control issuance means that, during a major economic crisis, the state cannot adjust the economy by increasing or reducing the money supply, as happened during the 2008 financial crisis. An inability to control transactions also allows far more illicit and underground transactions to flourish.

Furthermore, decentralization means that every full node in the community must store all transaction data. As the number of transactions grows, so does the data volume, continually increasing the storage and computing requirements imposed on community members.

# What Is Blockchain?
Blockchain is one way to implement decentralized money. Combined with cryptographic techniques such as asymmetric encryption, it can implement decentralized cryptocurrency. Several misconceptions need clarification: cryptocurrency is not necessarily decentralized, and decentralized money is not necessarily cryptocurrency. Gold, for example, is a classic decentralized, non-cryptographic currency. With modern digital money, however, a lack of encryption could let A impersonate B. Bitcoin and Trump-themed meme coins, among others, are therefore both cryptocurrencies and decentralized currencies.

A blockchain consists of individual blocks. Each block has two parts: a block header containing basic information and a block body primarily containing transaction data. There are two kinds of transaction. A coinbase transaction issues currency out of thin air and transfers it to an account. A regular transfer transaction moves money from account A to account B. Every full node in the community maintains the complete blockchain.

## A High-Level View of Blockchain
Technically, a blockchain is essentially a linked list. In a conventional linked list, the preceding block generally points to the next one, as shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/715e78c0_btc_img_01.png)

What makes a blockchain special is that the next block points back to the previous block. Instead of using a conventional memory-address pointer, it uses a hash pointer.

A hash pointer is essentially a hash value. Anyone with a computer science background knows that a hash algorithm maps a value X to another value Y through an irreversible process. A common algorithm such as SHA-256 maps an X of any size to a new, fixed-length 256-bit value Y.

When the next block b points to the preceding block a, block b is essentially recording the hash value of block a, as shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/ab2a1c74_btc_img_02.png)

One advantage is that if the contents of block a change, its hash value recorded in block b also changes. Block b then regards block a as invalid, breaking the chain. To keep the chain intact, a node storing it must alter block a and recalculate the hashes of every subsequent block, because each block's hash depends on the preceding block. This consumes enormous computing power—for example, under PoW, the node must redo the mining validation. The technical cost is extremely high. More significantly, even after completing the changes, the node must control over 51% of the entire network's computing power under PoW, or staked assets under PoS, to force other nodes to abandon the original valid chain and accept the altered version. The cost of such a 51% attack far exceeds any benefit from the alteration, making tampering virtually impossible.

This property of blockchain ensures that every block on the chain is **tamper-resistant**. That is really all there is to blockchain; nothing about it is inherently complicated. In one sentence, **a blockchain****<font style="color:rgba(0, 0, 0, 0.85);"> is an immutable database maintained jointly by decentralized nodes</font>**<font style="color:rgba(0, 0, 0, 0.85);"> (this “immutability” is not absolute; in theory, unlimited computing power could alter it, but in practice it is enough to ensure the authenticity and security of on-chain transaction records)</font>.

## Why Does Decentralized Money Need Blockchain?
Before discussing blockchain further, consider why decentralized money needs it. Since one of blockchain's major properties is immutability, the question becomes: why must decentralized money be immutable?

Trust in centralized money comes from the central bank's backing. People believe that a central bank will honor its debts and that banks will accurately record deposits. Even if banking-system data is altered, the central bank can use its authority to trace and correct it.  
Decentralized money has no central authority, and every node has equal power. Its “trust” can come only from the technical “authenticity of data.” If transaction records in a block could be altered at will—if A could secretly return a transferred 100 yuan to their own account, for example, or fabricate a transaction that takes B's money—the entire currency system's anchor of value would collapse instantly.

If decentralized transactions are technically immutable, then the data stored in their blocks can be trusted completely. Note that this trust is not the trust placed in a central bank under centralized money, but trust based on technical resistance to alteration.

## The Relationship Among Bitcoin, Blockchain, and Ethereum
Most people have heard something about Bitcoin, blockchain, and Ethereum, but how exactly do they differ?

Simply put, Bitcoin and Ethereum are both built on blockchain and both possess the characteristics of decentralized money. Although Ethereum can store and exchange value like a currency, its more important property is support for Smart Contracts.

Ethereum makes Smart Contract-based Apps distributed. A DApp's core logic, including transaction rules and asset ownership, can be packaged into blocks through Smart Contracts and then flooding-synced to every Ethereum node worldwide, while frontend resources may still be deployed on centralized machines. As a result, the application no longer exists on a single institution's server under the absolute control of an App vendor, as it did in the Web2 era. It exists across all node machines, and immutable Smart Contracts prevent even the App vendor from changing rules or manipulating data midway through execution. This is Web3.

# Bitcoin Based on a Blockchain Ledger
Blockchain guarantees that data cannot be tampered with. Building on that property, nodes running Bitcoin must also be capable of issuing currency, supporting valid transactions, and rejecting invalid ones—for example, when A has only 10 yuan but tries to transfer 100 yuan to B.

There are tens of thousands of Bitcoin nodes worldwide, all with equal authority. This section explores how Bitcoin uses blockchain and other specialized data structures to ensure that transactions and blocks are valid.

## Asymmetric Cryptography
> As mentioned earlier, Bitcoin is a cryptocurrency. We will therefore begin with some of the cryptographic algorithms involved in Bitcoin. We have already briefly discussed hash algorithms, so this section provides a short introduction to asymmetric cryptography.
>

Each blockchain block records a certain number of transfers. Suppose one transaction in a block transfers 10 BTC from Alice to Bob. From a cryptographic perspective, what encryption work must be done?

Consider Alice transferring money to Bob through Alipay. Before scanning the code to pay, Alice must enter a password to prove that the current Alipay account is really hers. This involves two steps: first, she sets a password in the centralized Alipay system before making the transfer; second, during the transfer, she enters that password and centralized Alipay verifies it.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/27e44fd0_btc_img_03.png)

Likewise, the initiator of a blockchain transaction must prove that she is Alice. First, Alice should set a password for this transaction. In blockchain, this act is called signing, just as a credit-card receipt may require a signature. When the transaction is about to be packaged into a block, the block performs the second step: verifying the signature's authenticity.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/23123fe5_btc_img_04.png)

Because Bitcoin is decentralized, individual nodes cannot store account passwords; if nodes stored those passwords, every account password would be exposed. Asymmetric cryptography makes it possible to sign and verify without revealing a password, thereby authenticating the user.

> Asymmetric cryptography uses public and private keys. Readers with computer-related backgrounds likely know that HTTPS is based on asymmetric cryptography. Its simplified process is: 1) the client uses the server's public key as the key to asymmetrically encrypt content, then transmits it to the server; 2) the server asymmetrically decrypts the content with its own private key.
>

From the HTTPS process, we can see that the essence of asymmetric cryptography is the one-to-one relationship between a public key, which is disclosed, and a private key, which remains secret. It has two primary scenarios: 1. Encryption: a public key encrypts data, and only the private key can decrypt it, as in HTTPS transmission; 2. Signing: the private key encrypts data such as transaction information to produce a “signature,” and anyone can use the public key to decrypt the signature and verify that the data came from the private-key holder. Together, these scenarios support Bitcoin's transaction security.

## Bitcoin Accounts
Based on these properties of asymmetric cryptography, when Alice transfers money to Bob, Alice must 1) write the transaction information; 2) sign her transaction with her private key; and 3) include her public-key information so nodes can verify the transaction signature when packaging it into a block.

We can therefore easily determine how a Bitcoin account is uniquely identified: its account credentials, analogous to a bank-account number and password, are a **public-private key pair conforming to asymmetric cryptography**. The public key is disclosed for receiving funds and representing the owner's identity. The private key is kept by the user and used to sign transactions. If someone steals your private key, they can easily transfer the money from your account. Because the system is decentralized, no institution can recover the money even after someone else transfers it away.

This raises a question: how do we determine the balance of a Bitcoin account?

In a centralized banking system, a relational database such as Oracle or MySQL can store mappings between accounts and balances. When a user makes a transaction, the centralized system need only run a simple update statement. But in a decentralized system, how can we ensure that every node updates every account affected by transactions in a block? How can we ensure that account data is consistent across nodes?

This is extremely difficult. We also know that blockchain data cannot be updated once inserted because of its immutable design. An account balance therefore cannot be updated on the Bitcoin blockchain. How can it be represented?

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c5e69815_btc_img_05.png)

As shown above, it can be calculated from a transaction ledger. The blockchain records every transaction, including the sender and recipient of BTC. Adding up the transaction records gives the account's balance. This explains this section's title: Bitcoin is a cryptocurrency based on a blockchain **ledger**. Ethereum is account-based and has a more complex MPT design, which is outside this article's scope.

## Blockchains, Nodes, and Accounts
The preceding section introduced Bitcoin accounts. Beginners may be confused about whether an account that initiates transactions is equivalent to a node, and whether every node must maintain a blockchain.

One point must be made clear: accounts and nodes have no necessary relationship. A node is a machine that runs the blockchain. Every node is equivalent and runs the same blockchain. Blocks in the blockchain package information about transactions between accounts. A person without any account can still run a blockchain node, although there is no reward and therefore no reason to do so.

For example, Alice has an account containing the public key PublicA and private key PrivateA. She owns a machine containing the complete blockchain. That machine is a Bitcoin node.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9beb844a_btc_img_06.png)

There is a problem: as the number of transactions grows, the complete chain requires more storage. If every node stores all information in the chain, every node needs a machine with enormous storage capacity, making Bitcoin prohibitively difficult to use. To allow even a phone to act as a blockchain node and make the system accessible to everyone, the Bitcoin protocol divides nodes into full nodes and lightweight nodes.

A full node stores all blockchain information and validates every transaction and block. Some full nodes participate in packaging blocks, or mining; these are called “miners.” A lightweight node does not store transaction details, only the header of each blockchain block. It can synchronize valid blocks from full nodes but does not write transactions.

# Bitcoin's Data Structures
## The Structure of a Single Block
We now know that lightweight nodes store only blockchain block heads, while full nodes store both block heads containing metadata and block bodies containing all transaction information, as shown below. For the exact contents of a recent real block, visit [OKLink](https://www.oklink.com/bitcoin/block/914370):

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/f67db3e0_btc_img_07.png)

Several details deserve emphasis. The hash pointer discussed earlier is not a hash of all the data in the preceding block. Suppose block b follows block a. Block b obtains block a's hash through this process:

1. When block a is generated, all its transactions are first processed through a Merkle Tree, discussed below, to calculate the final Hash of all transactions, the Merkle root, which is written into its block header.
2. Block a then calculates a Hash of its complete header, including the transaction hash and the preceding block's Hash, producing “block a's block-header Hash.”
3. When block b is generated, “block a's block-header Hash” is written directly into block b's header, forming the chain relationship.

## The Data Structure of Transactions in a Block
Besides blockchain itself, does Bitcoin use other specialized data structures?

It does. Suppose Alice transfers 10 BTC to Bob. How does Bob know that the money has reached his account? With centralized money, Bob can ask a bank. In Bitcoin's decentralized setting, if Bob owns a full node, it can traverse all nodes to check whether a transaction says “Alice transferred 10 BTC to Bob.” But what if Bob has a lightweight node, which holds only each block's head and no transaction information?

Bob's lightweight node can only ask an arbitrary full node on the P2P network whether an “Alice transferred 10 BTC to Bob” transaction exists. But because Bitcoin is decentralized, no node is theoretically trustworthy. Suppose Bob's lightweight node happens to query Alice's full node and Alice's node replies that the transaction exists when it actually does not. Bob has effectively been deceived.

How can this be solved? By using a Merkle Tree to maintain the structure of all transactions.

### Merkle Tree
A Merkle Tree is constructed by hashing transactions in pairs, hashing the resulting hashes in pairs, and continuing recursively until a single root hash, called the Merkle root, remains. All transactions and all hashes generated during this process form a Merkle Tree, as shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5f5ac865_btc_img_08.png)

The diagram shows that changing a transaction's hash propagates upward and changes the Merkle root. Because the Merkle root is included in the block header, changing it alters the block header's hash pointer, which in turn affects every successor block. Accomplishing this is virtually impossible.

A Merkle Tree has a useful property: given some hash values, namely a Merkle path, one can verify whether a particular transaction exists. In the diagram above, if a lightweight node wants to verify that transaction TX1 exists, the full node need only provide the hash values for TX2, H(2), and H(34). The lightweight node can calculate the Merkle root and compare it with the hash in its own block header. If they match, transaction TX1 really exists.

In practice, if Bob's lightweight node wants to verify that transaction TX has been packaged into a block by a full node, the process is:

1. Bob's lightweight node asks an arbitrary full node on the P2P network to verify transaction TX. Then
2. That node returns the Merkle path for transaction TX to Bob. Then
3. Bob's lightweight node independently calculates the “Merkle root” from “TX's Hash + the Merkle path” and **compares it with the Merkle root stored in its own block header**. If they match, TX truly exists in the block; if they differ, the path returned by the full node is invalid.

Lightweight nodes omit transaction information, but still store every block header in the blockchain, and each header contains a Merkle root. Their validation process essentially compares the correct Merkle root in their own block with the root calculated from the transaction and Merkle path.

## Overview of Bitcoin's Data Structures
What exactly does each Bitcoin full node look like? How does it organize its blocks? Where is the Merkle Tree stored?

The following diagram reveals the data structures inside each full node:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/424a115c_btc_img_09.png)

(Note that the block data in every full node's blockchain is identical.)

# Bitcoin's Consensus Mechanism
Before analyzing the details of Bitcoin transactions, we must consider how Bitcoin, the original decentralized currency, 1) enables every node to reach consensus and ensures that every node has consistent blockchain data, and 2) prevents malicious nodes from spreading invalid transactions to normal nodes.

These technical problems are solved using transaction pointers, UTXO, and a multi-node consensus protocol.

## Proof of Work (PoW)
Because Bitcoin is decentralized, every node maintains a blockchain. As noted earlier, every node's blockchain should contain identical blocks and transaction data. Yet every node is independent, so Bitcoin needs **a mechanism through which every node recognizes the block data produced by one node**. When node A forms its next block, all other nodes must follow that decision, abandon the blocks they were packaging themselves, and use node A's block as the next block in their own blockchains.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/8e367f8b_btc_img_10.png)

When transaction volume is high, node A may package transactions a, b, and c into its block while node B packages b, d, and f into its own. Which of those two blocks should the other nodes follow? In Bitcoin, Proof of Work solves the problem of making every other node recognize a newly packaged block from one node.

When a Bitcoin node's software generates a new block, it sets a difficulty value X. To package the block, each node must calculate the hash of its “block header,” which contains the preceding block's hash, Merkle root, timestamp, difficulty target, nonce, and other data. The resulting hash value Y must meet the specific requirement imposed by difficulty X. Because a hash value is unpredictable, a node can only keep changing the nonce and repeatedly calculating until it obtains a value Y that meets X. Only then is the new block considered valid and eligible to be accepted by other nodes after broadcast. **This process of trying different nonce values until Y satisfies X is called Proof of Work (PoW)**.

Every 2,016 blocks, the Bitcoin system dynamically adjusts difficulty X according to the total computing power of all nodes, keeping the average block-packaging time near ten minutes. A transaction therefore takes about ten minutes to be published to the blockchain, while confirmation requires waiting for six subsequent blocks, or roughly an hour. This cannot begin to compare with Alipay's routinely hundreds of thousands of TPS. The process in which nodes calculate Y to package a block is called mining, and the nodes that do it are called miners.

### Why Use PoW?
Some may ask why every miner should compete for the right to publish blocks through PoW's seemingly pointless computation. It simply wastes computing power and electricity; even after the Yarlung Tsangpo dam is completed, it might not withstand consumption on this scale.

Why not use time? Why not simply follow whoever publishes a block first?

That does not work, for two reasons:

1. Each node can be regarded as an independent computer. When relying only on local clocks, times can differ across machines, and a node could even deliberately set its local clock ahead. Different nodes would then disagree about the latest time.
2. If blocks were packaged based on time, large numbers of different blocks would be published to the network during the same period, creating many forks. Yet **only the longest chain can be treated as valid**. Many published blocks would consequently be useless, wasting computing power and harming the Bitcoin community.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/23b7f548_btc_img_11.png)

As the blockchain community has developed, Ethereum has introduced a voting mechanism that does not waste computing power, Proof of Stake (PoS). This article focuses on Bitcoin, so PoS will not be discussed further.

### Why Do Miners Mine?
Why would miners waste vast amounts of computing power on mining? Are they simply overflowing with geek spirit and volunteering to package every community transaction into a block? Clearly not. To sustain a thriving community, when miners package transactions into blocks, the system rewards the first miner to calculate a nonce that meets the difficulty requirement. Besides allowing that miner to package and publish the block, it grants the miner a BTC reward.

Unlike a transfer, this reward has no input; **it generates new Bitcoin “out of thin air”**. This is what we commonly call a **coinbase transaction**. Through such transactions, Bitcoin acquires the ability to issue currency.

Bitcoin distributes a block reward about every 10 minutes, and the reward halves every 4 years, or 210,000 blocks. The current reward is 3.125 BTC per block. At Bitcoin's current [price](https://www.oklink.com/bitcoin) of USD 110,000 per coin, publishing one block earns a miner USD 360,000—more than an ordinary person may earn in a lifetime.

## Valid Transactions
We noted earlier that if Alice transfers 10 BTC to Bob, she must sign the transaction with her private key. Other nodes use Alice's public key to verify it, and the transaction is valid only if verification produces the expected result.

Because Bitcoin is ledger-based and has no account concept, however, asymmetric cryptography verifies the transaction initiator's identity but not whether the initiator has sufficient funds. Two situations require attention:

1. <u>Suppose Alice previously earned a 10 BTC block reward from mining and tries to transfer 20 BTC to Bob. How does a block reject the transaction?</u>
2. <u>Suppose Alice previously earned a 10 BTC block reward from mining, already transferred 10 BTC to Bob, and later attempts to transfer another 10 BTC to Bob. How does a block reject it?</u>

### Transaction Pointers
The solution is simple. When publishing a transaction, Bitcoin requires the sender to use a hash pointer to point that transaction to the earlier transaction through which the sender obtained the Bitcoin, as shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/22a079e5_btc_img_12.png)

The node packaging the transaction can then easily use the hash pointer to find the transaction through which Alice obtained her BTC and validate it. “Alice transfers 20 BTC to Bob, but Alice previously received only 10 BTC” is invalid, so validation fails. This solves the first problem.

The second problem remains. Suppose Alice creates TX2 immediately after TX1 and transfers another 10 BTC to Bob, as shown below. A transaction pointer alone cannot detect this “double-spend transaction.” Nodes therefore need to maintain state recording whether the BTC output from each transaction has already been spent.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/fd9c71b0_btc_img_13.png)

### UTXO
The data structure that records whether transaction outputs have been spent is called Unspent Transaction Output (UTXO).

UTXO can be understood as a map keyed by transaction and recipient, whose value records whether another transaction has spent the current transaction's output. In the diagram above, TX0 gives Alice a 10 BTC block reward, so the UTXO for the block containing TX0 is `{'TX0:Alice': false}`, indicating that TX0's output has not been spent. Once TX1 is packaged into a block, the UTXO for the block containing TX0 becomes `{'TX0:Alice': true}`, indicating that TX0's output has been spent. If TX2 later points to TX0, validation finds that TX0's output has already been spent and classifies TX2 as invalid, so it is not packaged into a block.

Unlike the immutable blockchain, this UTXO can change. It is not part of the blockchain and does not participate in hash calculations. Nodes **do not** synchronize their block's UTXO state to other nodes over the network. Instead, each node locally constructs UTXO whenever it updates its blocks. As new blocks are added, UTXO changes dynamically according to the transactions in the blockchain.

UTXO exists to help nodes validate transactions more quickly. Without it, a node trying to prevent a “double-spend transaction” would have to traverse every transaction in every block from newest to oldest. With about 910,000 blocks today, even a single traversal would impose considerable computational cost.

## Valid Blocks
Transaction pointers and UTXO let a node accurately determine whether transactions are valid while packaging a block. Only valid transactions are packaged. If an abnormal node packages an invalid transaction into its block, the other nodes on the network will not recognize that block.

But if every transaction in a block is valid, will the other network nodes necessarily accept it? No. Valid transactions are only a necessary condition for a valid block. Validating a block also requires the PoW described earlier.

### How to Validate a Block
After a node publishes a block to the network, other nodes verify its PoW by calculating the hash from the block header's nonce, pre hash, Merkle root, and other fields and checking whether it meets the mining difficulty. If the Proof of Work is valid, they then validate each transaction using transaction pointers and UTXO. Only when every transaction in the block is valid do the other nodes recognize the block as valid.

Yet a valid block is not necessarily accepted by the other nodes.

Consider a node that produces a valid new block A whose transactions are also valid, but whose pre hash points to a block from several years ago, as shown below. Will other nodes accept it?

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/72ca1d6d_btc_img_14.png)

They will not. A Bitcoin blockchain may have multiple forks, and because transactions can differ across forks, multiple branches cannot all be valid. Bitcoin recognizes only one blockchain as valid: the longest one, meaning the one with the greatest accumulated work. When block A pointing to a very old block is published to the network, other nodes compare the work difficulty of block A's chain with the accumulated work difficulty of their own local chain. If A's chain has less work, block A is discarded without mercy. Its transactions do not achieve consensus on the Bitcoin network, and the node that produced A mined for nothing.

To avoid this, whenever a miner discovers a blockchain longer than its own on the network, it must immediately update the pre hash of the block it is packaging and recalculate the nonce and other parameters to complete PoW again.

### What If Valid Blocks Are Produced Simultaneously?
Because mining is nondeterministic, two nodes may produce valid blocks with equal work at the same time, as shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/d01e1eab_btc_img_15.png)

Other nodes will initially accept both blocks A and B because they contain the same amount of work. Due to network uncertainty, however, some nodes will mine from BLOCK A while others mine from BLOCK B. If a new block is mined after BLOCK A first, the other nodes regard the chain containing BLOCK A as the longest valid chain and discard BLOCK B. Once BLOCK B is discarded, its coinbase transaction awarding currency to the corresponding account also becomes invalid.

To prevent uncertainty over which node's transactions to follow when two nodes produce blocks simultaneously, Bitcoin's real-world payment rule considers transactions in BLOCK A valid only after six additional blocks have been added behind it.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/853decfb_btc_img_16.png)

Thus, **Bitcoin is a consensus game decided by every node in the community, rather than a sovereignty game decided by a central institution**. That may be the appeal of decentralization.

# The Lifecycle of a Bitcoin Transaction
Using the consensus mechanism and Bitcoin data structures described in this article, let us reconstruct how every node in the Bitcoin network changes when “Alice transfers 10 BTC to Bob”:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/9fd2ee78_btc_img_17.svg)
