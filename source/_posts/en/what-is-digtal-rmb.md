---
title: Why the Digital Renminbi Matters in an Online Payment Economy
tags:
  - 支付与结算
categories:
  - 基础夯实
date: 2025-09-17 10:36
description: >-
  Starting with the separation of information flow and fund flow in conventional
  online payments, this article clarifies transaction, clearing, settlement, and
  delivery, and explains how the digital renminbi synchronizes fund flow through
  central-bank blockchain technology and its use cases.
lang: en
translation_of: what-is-digtal-rmb
---

# Preface

I have recently been developing cross-border payment and fund-related features. Cross-border fund movement is truly expensive and slow, although domestic consumers hardly feel those drawbacks. That led me to study China's online-payment network, as well as the digital renminbi and stablecoins.

Some readers probably have a digital-renminbi bank account. Yet most people ask the same question when using it: paying with the digital renminbi feels almost identical to Alipay. Since we already have online payment as convenient as Alipay, why is the country promoting it?

Some guess it is redundant and merely creates jobs. Others think the state wants to take control of electronic payments back from Alipay and WeChat. Some even think it is only a blockchain gimmick for capital markets.

In fact, its strategic value goes far beyond what most people imagine. The digital renminbi has been digital from its creation, which is very different from traditional paper RMB supported by the Internet.

From a user's perspective, the digital renminbi and Alipay are both quick and convenient online payments. But in areas such as large-value transactions, which ordinary consumers rarely encounter, conventional RMB online payment still has many pain points.

This article begins with online payments, discusses the difference between conventional RMB and the digital renminbi, and finally considers the opportunity for stablecoins in mainland China.

# The nature of conventional online payments
> Conventional online payments complete transactions through digitized banknotes. Underneath, RMB still needs to move among banks.
>

## Information flow and fund flow
Before online transactions became widespread, everyone transacted offline directly with RMB. <font style="color:rgb(15, 17, 21);">When we hand cash to a merchant, the delivery of funds and goods is completed simultaneously. This is the familiar idea of “</font>**<font style="color:rgb(15, 17, 21);">payment and goods settled together</font>**<font style="color:rgb(15, 17, 21);">”; the transaction's information flow and fund flow also finish together.</font>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/91a95a98_nlark_img1.png)

<font style="color:rgb(15, 17, 21);">Keeping cash on hand is inconvenient, so most money is held in banks. Withdrawing it to buy goods offline is troublesome. Naturally, we want to pay directly online through banks, as shown below.</font>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/95ed4685_nlark_img2.png)

<font style="color:rgb(15, 17, 21);">But is the solution really that simple? What if Li Si's account is at another bank?</font>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/3777b175_nlark_img3.png)

Bank A must actually transfer Zhang San's 10 yuan to Bank B; this is called fund delivery. Delivery cannot be completed by a simple instruction, so interbank transfers are slow. Can they be made faster?

Yes. Bank A can open an account at Bank B and deposit a reserve. When Zhang San asks Bank A to transfer 10 yuan to Bank B, Bank A only sends the instruction and Bank B debits A's account. This is clearly much more efficient.

<font style="color:rgb(15, 17, 21);">This approach still leaves at least two issues unresolved:</font>

1. **<font style="color:rgb(15, 17, 21);">The obstacle of transfers among many banks</font>**<font style="color:rgb(15, 17, 21);">: China has hundreds of commercial banks. Must every bank deposit funds with every other? A bank failure or disappearance could cause a major incident, which the state does not want.</font>
2. **<font style="color:rgb(15, 17, 21);">Lack of supervision and restraints</font>**<font style="color:rgb(15, 17, 21);">: without effective supervision, commercial banks may face moral hazard, such as transferring Li Si's funds to Zhang San without authorization.</font>

<font style="color:rgb(15, 17, 21);">Therefore, a highly trusted intermediary is needed. This role is performed by the People's Bank of China (PBOC). The PBOC requires online payments and transfers to go through UnionPay (interbank transactions) or NetsUnion (transactions involving payment institutions); those systems settle the funds. Commercial banks and payment institutions must also maintain reserve accounts at the PBOC, which completes final fund delivery.</font>

<font style="color:rgb(15, 17, 21);">Modern online payments can therefore be roughly divided into two steps:</font>

1. **<font style="color:rgb(15, 17, 21);">Information flow</font>**<font style="color:rgb(15, 17, 21);">: payment institutions or banks make internal book entries and freeze the funds, completing preliminary processing.</font>
2. **<font style="color:rgb(15, 17, 21);">Fund flow</font>**<font style="color:rgb(15, 17, 21);">: funds are actually moved through the central-bank clearing system; only then does ownership truly transfer.</font>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/266325f4_nlark_img4.png)

This is the information flow and fund flow often mentioned in payments. Online payment is much more complex than it looks. Can such a complex process finish in seconds?

**Clearly it cannot.** Every transaction must be handled by the central bank. If it updated every bank's reserve account in real time for each transaction, its system would quickly collapse. The PBOC instead uses T+1 batch processing and netting for daily transactions between banks and payment institutions. The information flow can finish quickly, but the fund flow through the PBOC may take a day to become final.

Why then does an Alipay transfer feel instantaneous to consumers? Alipay provides credit backing and advances funds. Because it has reserve accounts at partner banks, it can notify relevant banks to pre-debit funds during the information-flow stage. In general, **when users see a transaction succeed in real time, only the information flow has succeeded**; the fund flow still needs central-bank settlement.

## Transactions, clearing, settlement, and delivery
To understand what happens behind a payment, we need to clarify transaction, clearing, settlement, and delivery.

1. **<font style="color:rgb(15, 17, 21);">Transaction</font>**<font style="color:rgb(15, 17, 21);">: here this does not mean buying and selling goods, but the</font>**<font style="color:rgb(15, 17, 21);">initiation of a payment instruction</font>**<font style="color:rgb(15, 17, 21);">. It specifies sender, recipient, amount, and other information, and starts the fund process. Clicking “Confirm payment” in Alipay initiates a</font>**<font style="color:rgb(0, 0, 0) !important;">fund-transfer instruction</font>**<font style="color:rgb(0, 0, 0);">.</font>**<font style="color:rgb(0, 0, 0);">From the user’s view, “Success” means the instruction has been received, not that fund transfer is over.</font>**<font style="color:rgb(0, 0, 0);"> Participants include the</font>**<font style="color:rgb(0, 0, 0) !important;">user initiating it</font>**<font style="color:rgb(0, 0, 0);"> and the payment institution or bank receiving it.</font>
2. **Clearing**: <font style="color:rgba(0, 0, 0, 0.85);">the</font>**<font style="color:rgb(0, 0, 0) !important;">centralized handling of many transactions over a period</font>**<font style="color:rgba(0, 0, 0, 0.85);">. It verifies transaction information, calculates each party's receivables and payables, and establishes the claims and obligations between payment institutions and banks (the net amount). In short, it calculates who owes whom how much; an obligation is established but funds have not moved. Participants are mainly</font>**<font style="color:rgb(0, 0, 0) !important;">clearing institutions such as NetsUnion and UnionPay, banks, and payment institutions</font>**<font style="color:rgba(0, 0, 0, 0.85);">.</font>
3. **<font style="color:rgb(15, 17, 21);">Settlement</font>**<font style="color:rgb(15, 17, 21);">: the process of</font>**<font style="color:rgb(15, 17, 21);">final confirmation</font>**<font style="color:rgb(15, 17, 21);"> of clearing results and creation of irrevocable transfer instructions. It makes obligations final. Clearing and settlement are often jointly called “clearing,” normally comprising “calculate the accounts” and “pay the money.” Participants extend to the</font>**<font style="color:rgb(15, 17, 21);">central bank</font>**<font style="color:rgb(15, 17, 21);"> payment system.</font>
4. **Delivery** **<font style="color:rgba(0, 0, 0, 0.85);">(Settlement finality)</font>**: <font style="color:rgba(0, 0, 0, 0.85);">when settlement is complete and transfer is irrevocable, delivery has been reached.</font><font style="color:rgb(15, 17, 21);"> It is the</font>**<font style="color:rgb(15, 17, 21);">final stage</font>**<font style="color:rgb(15, 17, 21);">, achieving</font>**<font style="color:rgb(15, 17, 21);">settlement finality</font>**<font style="color:rgb(15, 17, 21);">. The central bank adjusts the balances of the relevant</font>**<font style="color:rgb(15, 17, 21);">commercial banks</font>**<font style="color:rgb(15, 17, 21);"> in their</font>**<font style="color:rgb(15, 17, 21);">reserve accounts</font>**<font style="color:rgb(15, 17, 21);">. Only then have funds fully transferred in law. A payment institution's</font>**<font style="color:rgb(15, 17, 21);">centralized customer-reserve custody account</font>**<font style="color:rgb(15, 17, 21);"> is adjusted correspondingly, ultimately affecting its custodian bank’s reserve account.</font>

<font style="color:rgb(15, 17, 21);">Typical processing times:</font>

| **<font style="color:rgb(0, 0, 0) !important;">Stage</font>** | **<font style="color:rgb(0, 0, 0) !important;">Time window</font>** |
| :---: | --- |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">Transaction</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">24/7 (users may initiate payment instructions at any time)</font> |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">Clearing</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">Real-time clearing (D0) or scheduled clearing (such as early morning T+1, chosen by the payment institution)</font> |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">Settlement</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">24/7 (small-value / third-party payments) or weekdays 8:30–17:00 (large-value system, traditional mode)</font> |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">Delivery</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">Real-time after settlement (account balances update immediately)</font> |

## Fund movement in online payments
Suppose user A transfers 100 yuan from a China Merchants Bank account to user B's Alipay balance. Each stage is:

1. **<font style="color:rgb(15, 17, 21);">Transaction:</font>**<font style="color:rgb(15, 17, 21);"> A clicks pay in Alipay, which sends an instruction to China Merchants Bank, and the bank freezes A's amount.</font>**<font style="color:rgb(15, 17, 21);"> A sees payment succeed and B receives money, but Alipay has only made internal entries; funds have not truly moved.</font>**
2. **<font style="color:rgb(15, 17, 21);">Clearing:</font>**<font style="color:rgb(15, 17, 21);"> Alipay packages transactions from a period and sends them to NetsUnion, which calculates how much Alipay should receive from CMB and pay other banks (netting).</font>
3. **<font style="color:rgb(15, 17, 21);">Settlement:</font>**<font style="color:rgb(15, 17, 21);"> NetsUnion turns the calculated net result (for example, Alipay receives a net 100 yuan from CMB) into a formal settlement list and sends it to the PBOC payment system.</font>
4. **<font style="color:rgb(15, 17, 21);">Delivery:</font>**<font style="color:rgb(15, 17, 21);"> The PBOC’s large-value payment system completes the transfer</font>**<font style="color:rgb(15, 17, 21);">finally and irrevocably</font>**<font style="color:rgb(15, 17, 21);"> on its ledger: it debits 100 yuan from CMB's reserve account and credits Alipay's reserve account.</font>**<font style="color:rgb(15, 17, 21);"> Only then has A's 100 yuan actually left CMB and entered Alipay's pool.</font>**

<font style="color:rgb(15, 17, 21);">The flowchart makes the full fund movement easier to see:</font>

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/610f57ff_nlark_img5.svg)

## Drawbacks of online payments
Conventional RMB is essentially cash; online payments merely digitize it. Ordinary people cannot digitize cash and trade online by themselves, so they deposit money in banks and use banks or payment institutions as intermediaries.

Intermediaries create these drawbacks:

**Poor timeliness:** Although small transfers seem instant to both parties, that only completes the transaction stage; the fund flow has not finished. Large-value transfers still need T+1 (withdrawals commonly arrive T+1). If domestic large-value transfers take T+1, international transfers take even longer; USD-to-PKR may take a week.

**High fees:** Alipay and WeChat charge withdrawal fees (0.1%). Cross-border transfers can involve more intermediary banks and average around 7% in fees.

**Difficult account opening:** Offline, cash is enough. Online, an account must be opened at a bank or payment institution, with identity registration and review. This is unfriendly to overseas travelers and visitors from elsewhere.

**Network dependence:** Current online payments rely on the Internet. Without it, online transactions are impossible.

**Institutional risk:** Online payments rely on banks and payment institutions. If they disappear or fail, users' funds may change hands.

The digital renminbi emerged to address these drawbacks.

# The underlying logic of the digital renminbi
## Its nature
Unlike conventional RMB, which is still essentially physical cash, the digital renminbi uses blockchain capabilities and is digital from inception. In theory, its online transactions need no intermediary bank or payment institution.

For example, Zhang San can transfer 10 yuan of digital RMB directly to Li Si through their electronic wallets, just as handing over 10 yuan in cash. The record is written directly to a blockchain operated by the PBOC; no payment institution or bank participates.

In one sentence: conventional RMB online transactions, such as online banking and Alipay, separate a first-completed information flow from a later-completed fund flow. Digital-RMB online transactions, like conventional RMB offline transactions, unify both flows and complete them simultaneously.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/2a1aec14_nlark_img6.png)

### Blockchain and smart contracts
The digital renminbi is based on blockchain technology. What is a blockchain?

Think of it as a special linked list. Unlike an ordinary linked list, changing information in any blockchain node requires changing every following node to produce a valid chain again. Because such changes are extremely costly (almost impossible), a blockchain is essentially an immutable database.

For an article on blockchain, see:

[A 10,000-word introduction to blockchain and Bitcoin · Yuque (in Chinese)](https://www.yuque.com/wangxingxing-f4sey/iur8x3/mekvlarxoaw58uvb)

Because it cannot be modified, once user transaction data is stored on a blockchain, we can trust the authenticity of account balances derived from it.

A smart contract can be understood as a contract running on a blockchain. It is tightly bound to the currency on that blockchain. Code can specify when it automatically transfers money to someone. Once published, it cannot change; when a specified condition is triggered, it transfers money to a specified account.

### Digital RMB and Bitcoin
<font style="color:rgb(15, 17, 21);">Based on blockchain and cryptographic algorithms, both digital RMB and Bitcoin are cryptographic digital currencies, but they differ fundamentally.</font>

<font style="color:rgb(15, 17, 21);">The central difference is that</font>**<font style="color:rgb(15, 17, 21);">Bitcoin is completely decentralized</font>**<font style="color:rgb(15, 17, 21);">: any participant can operate a node, and transaction information is fully public. By contrast,</font>**<font style="color:rgb(15, 17, 21);">digital RMB uses a centralized architecture</font>**<font style="color:rgb(15, 17, 21);"> whose blockchain nodes are entirely controlled by the PBOC, protecting transaction records and account balances.</font>

<font style="color:rgb(15, 17, 21);">In terms of value,</font>**<font style="color:rgb(15, 17, 21);">Bitcoin fluctuates sharply</font>**<font style="color:rgb(15, 17, 21);">: from the original 1,250 BTC for a pizza to as much as US$110,000 per coin, its price is highly uncertain.</font>**<font style="color:rgb(15, 17, 21);">Digital RMB is stable</font>**<font style="color:rgb(15, 17, 21);">: as central-bank digital currency, it is backed by national credit, exchanged at par with paper RMB, and has unlimited legal-tender status.</font>

<font style="color:rgb(15, 17, 21);">As to issuance,</font>**<font style="color:rgb(15, 17, 21);">Bitcoin supply is fixed</font>**<font style="color:rgb(15, 17, 21);"> at 21 million from inception and is controlled by no institution.</font>**<font style="color:rgb(15, 17, 21);">Digital RMB issuance is flexible</font>**<font style="color:rgb(15, 17, 21);">: like conventional RMB, it is macro-regulated by the PBOC according to economic need.</font>

<font style="color:rgb(15, 17, 21);">Thus, despite both using cryptography, digital RMB is legal tender representing national credit; Bitcoin is decentralized crypto currency with more of an investment character. This is their most fundamental difference.</font>

## Digital-RMB applications
Returning to the original question: what does digital RMB have to do with ordinary people? After much thought, regrettably, not much. Competition from Alipay and similar institutions pushed banks to optimize online payments—small transfers are free and arrive in seconds—so consumers already have an excellent, fee-free experience.

In special circumstances, however, ordinary users can benefit. Without a network, online payments stop working. An electronic wallet on a physical device can pay digital RMB offline because balance information is local, then synchronize settlement with the PBOC once online. That means tourists in mountainous areas need not carry cash.

But the country would obviously not invest this effort merely for offline payment. The core is direct transactions between counterparties through the central-bank system, without intermediaries. Together with smart contracts, which can enforce transfers automatically under contractual terms, this creates different application scenarios.

### Cross-border use
Friends who trade US or Hong Kong stocks may know that domestic-to-foreign-bank transfers use SWIFT. Funds need clearing through the relevant central banks for USD, EUR, or RMB and through several intermediary banks. Each bank holds the funds and charges a percentage or fixed clearing fee.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/58c18f2d_nlark_img7.png)

International interbank transfers typically take at least T+1 and fees are often around 5%. Excluding risk-control review, digital RMB could arrive in real time and at very low cost because there are no intermediary banks. This would be a major benefit for cross-border trade, one of the three engines of growth.

The country is also promoting digital RMB in Belt and Road settings to reduce dependence on the US-centered SWIFT system. If countries across Asia and Africa accept it, cross-border trade—especially fund movement—could happen anytime and anywhere.

### B2B
For merchants, consumer payment in digital RMB transfers directly through the PBOC blockchain into the merchant's digital-RMB wallet. There are no payment institutions or intermediary banks, and thus no “withdrawal,” withdrawal fee, or slow arrival.

Smart contracts also bind contracts to fund flows automatically, making payment default less likely. For example, suppose Company A and Company B sign a procurement contract: when B receives A's product, B pays A RMB 1 million. Traditionally, the contract creates legal obligations; if B does not pay, A must use judicial procedures.

With digital RMB this could differ. A and B can create a coded smart-contract agreement. When a logistics company sends delivery information to the contract, it automatically transfers B's RMB 1 million to A's account, preventing non-payment.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/c22de5e6_nlark_img8.png)

Business is complex, however. <u>Not every acceptance criterion can be digitized. If Party A delays acceptance, the system cannot trigger the contract and the digital RMB in A's account still cannot settle to Party B.</u> Technology alone cannot solve this.

### G2B
Smart-contract rules can direct government digital-RMB fiscal allocations more precisely, preventing misuse and untraceability of conventional funds. For example, a poverty-alleviation program is intended for fertilizer and seeds. The government creates a subsidy smart contract and funds it. It specifies: 1) only designated farmers may use the subsidy, each with an allowance; 2) it lasts one year and unused subsidy returns automatically to the government; and 3) recipients must be agricultural merchants registered with the government.

After a farmer buys fertilizer and seed from a designated merchant, they enter the merchant information registered with the government. This notifies the smart contract to use the farmer's allowance, and it transfers the digital RMB to the merchant wallet.

If the farmer buys a Mac rather than agricultural goods, the contract has no Apple information, so funds cannot be sent to Apple.

Smart contracts therefore enable targeted subsidy use. This strengthens government control of subsidy funds and uses taxpayer money more efficiently.

# Digital RMB and stablecoins
With the US GENIUS Act enacted in recent months and Hong Kong's Stablecoins Ordinance formally taking effect, stablecoins have again created a market wave.

A stablecoin is essentially Bitcoin tied to fiat currency. For an article on Bitcoin, see:

[Seven images that explain what Bitcoin looks like (in Chinese)](https://www.yuque.com/wangxingxing-f4sey/iur8x3/vhm08q3mw87ocv4p)

<font style="color:rgb(15, 17, 21);">As crypto assets, stablecoins inherit some key Bitcoin characteristics:</font>

1. **Anonymity:** an account is a hash value and all transactions use hashes. Even if transactions are traceable on-chain, the real owner of a hash account cannot be known.
2. **Timeliness:** <font style="color:rgb(15, 17, 21);">transfers can complete in minutes, operate 24/7, and break traditional finance's time and geographic barriers without waiting days for clearing.</font>

Stablecoins are also pegged one-to-one to fiat money such as USD and HKD: when someone buys one yuan's worth, one stablecoin is created on-chain. <font style="color:rgb(15, 17, 21);">Compliant issuers must hold equivalent fiat reserves to ensure solvency.</font>

Their relatively stable market value plus decentralization, anonymity, and real-time settlement have made them popular.

<font style="color:rgb(15, 17, 21);">Globally, stablecoins have become a new arena of geopolitical finance:</font>

+ For the United States, the GENIUS Act regulates stablecoins redeemable one-to-one for dollars, meaning the US has begun recognizing them. Dollar stablecoin volume may grow explosively. Their anonymity allows even countries previously sanctioned by the US, such as Russia, to trade again with other countries using dollar-based stablecoins, further strengthening dollar hegemony.
+ For Hong Kong, they are an outlet for China's fund flows. Mainland trade funds, whether imports or exports, generally pass through Hong Kong. Its recognition of stablecoins further consolidates its role as a port city. HKD stablecoins can greatly increase cross-border trade-fund liquidity and lower costs.
+ For mainland China, digital RMB already has many stablecoin functions, such as real-time settlement, and adds programmability and central-bank backing. Mainland China is therefore unlikely to promote stablecoins. Its foreign-exchange controls also do not permit anonymous USD or HKD stablecoins to circulate domestically.

In one sentence, stablecoins are an opportunity—but across the ocean. In mainland China, it is worth watching the digital renminbi more closely.
