---
title: How Cross-Border E-Commerce Transactions Work
date: 2026-01-04 14:16
tags:
  - 跨境电商
  - 支付与结算
categories:
  - 业务学习
description: >-
  An in-depth analysis of the full fulfillment flow on cross-border e-commerce
  platforms. It examines how information, funds, and logistics work together
  from buyer and seller perspectives, and reveals platform profit models and
  fund-settlement systems.
lang: en
translation_of: cross-border-ecommerce-transaction-flow
---

As someone who spends time surfing the Internet, I use online shopping platforms such as Taobao, JD, and Pinduoduo for everyday purchases.

Since changing roles in August 2024, I have been responsible for online-shopping business similar to Taobao and JD, but with two differences. First, Taobao and JD are B2C shopping platforms for ordinary consumers, while the code I write serves B2B trade platforms. Second, Taobao and JD serve domestic merchants and consumers, whereas I work with overseas merchants and overseas consumers every day.

Over the past year, the code I developed has covered merchant onboarding, transactions, orders, safeguards, payments, settlement, liquidity, accounting, gateways, and other domains. As my first article of 2026, this is a summary of roughly the past year of work. It also explains the complete cross-border transaction-fulfillment flow.

# What buyers and sellers do on e-commerce platforms
The essence of online transactions on e-commerce platforms is managing the flow of information, funds, and logistics: 1) transactions carry the information agreed by buyers and sellers; 2) funds legally and compliantly transfer buyers’ payment to sellers’ cards; and 3) logistics safely transports sellers’ goods to the locations buyers specify.

Below is a brief summary from buyer-seller and platform perspectives.

## Buyer and seller perspective — the transaction lifecycle
The end-to-end view from buyers’ and sellers’ perspective is as follows:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/5606db74_ab1a042e.png)

The preceding diagram shows a **release of funds** action after the buyer completes payment. Payment cannot go directly into the seller’s account because we cannot guarantee that the seller will fulfill normally afterward. If you have noticed, when you confirm receipt on Taobao, you are asked to enter your payment password (or complete Alipay facial verification). That is because for Taobao, your money is truly paid to the merchant only when you confirm receipt.

From buyer and seller perspectives, the following are the main action points:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/59b28626_e8a5f5e5.png)

## Platform perspective — the platform’s role in a transaction
From the platform’s perspective, the key is to connect the flows in different business domains across transaction and fund stages. A simplified flowchart is as follows:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/3ebf4508_2a52ab59.png)

# E-commerce participants and profit models
## Participants — many pairs of eyes behind a transaction
For ordinary consumers, this is simply a transaction completed by buyer and seller on a platform. From the platform’s perspective, though, transaction participants include not only the platform and buyer and seller, but also various intermediary funding channels.

Taking a basic cross-border online trading platform as an example: if the platform is not licensed to handle buyers’ funds, then in addition to buyers, sellers, and the platform, an extra funding center is needed. The arrangement is as follows:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/1afff81c_7693194e.png)

Once a platform has the license to hold funds, it often has the acquiring institution settle funds to the platform to strengthen its control over funds; the platform then settles those funds to sellers worldwide through a payout institution.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/367b905e_407deea6.png)

Every participant should be bound by an agreement with the others.

Buyers need an agreement with the platform to purchase goods and pay for them; merchants need an agreement with the platform to trade goods and withdraw funds; Adyen, as the acquiring channel, also needs a corresponding acquiring agreement with the platform; Payout, as the payout channel, needs corresponding payment-service agreements with both the platform and merchants. If there is an FX institution (used to exchange foreign currencies into USD), that institution must also sign an agreement with the platform.

## Profit models — how platforms make money
From a consumer perspective, online transactions can charge merchants a transaction service fee on every transaction. In cross-border scenarios, however, platforms have many ways to profit:

1. Transaction dimension
    1. Transaction service fee: roughly a 3% technical service fee is charged to merchants for each transaction. This revenue belongs entirely to the platform; accordingly, the platform must issue an invoice to the merchant.
2. Payment dimension
    1. Payment processing fee: each payment charges the payer (buyer) a 3% fee (depending on the payment instrument). Unlike domestic payments, overseas payment instruments generally charge the payer a percentage on every payment (credit cards are basically 2%, for example). The platform shares revenue with the payment institution under a fixed rule.
3. Withdrawal dimension
    1. Withdrawal fee: every time a merchant withdraws funds from its platform balance account to a bank card, it is charged a fee at a fixed rate or amount. The platform generally collects it on behalf of the provider, then shares it with the payout institution. This applies both domestically and internationally: merchants pay fees whenever they withdraw. For example, Alipay and WeChat both charge a 0.1% withdrawal fee.
4. Value-added services
    1. Insurance premium: the platform can help merchants insure goods and share premiums with the insurance company.
    2. Loan interest: mature platforms partner with banks to offer loans to merchants, splitting loan interest with the channel.
    3. Collection service fee: by providing factoring institutions, platforms help merchants collect funds rapidly, sharing the service fee with the institution.
    4. Deposit: merchants often pay the platform a deposit when opening a store, used for deductions in subsequent after-sales disputes.
5. Merchant dimension
    1. Merchants joining Alibaba International Station as members need to pay a membership fee.
    2. Merchants can purchase many kinds of services to increase the exposure of their stores and themselves, thereby improving conversion. This is the profit core of virtually every online platform, such as Taobao’s Alimama and Douyin’s Ocean Engine.
6. Logistics dimension
    1. Merchants pay the platform a logistics fee when shipping; the fee is shared with logistics companies.

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/88f308d8_55e4f92c.png)

# Cross-border fund clearing and settlement
Transactions represent information flow; another important part is fund flow. At the lowest level, fund flow is the movement of money among financial institutions, accompanied by debit-credit relationships among accounts. Fund transfers and accounting give rise upstream to business scenarios such as merchant onboarding, payment, settlement, withdrawal, transfers, and foreign exchange.

## Fund flow — how your money reaches the merchant’s pocket
For a cross-border platform in its early construction phase, an acquiring platform can provide USD settlement capability to get the site running quickly, so there is no need to introduce an FX institution. Note that because this is a cross-border platform, under the current system of U.S.-dollar dominance, USD is the default preferred settlement currency.

The fund flow is shown below:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/129fbdba_99a72499.png)

**Phase one:** After placing orders, buyers around the world enter the payment process. They pay the acquiring institution (for example, Adyen) through CREDIT CARD, GOOGLE PAY, APPLY PAY, PAYPAL, and other local payment methods. Adyen then performs internal currency conversion and settles the funds to the platform entity at T+1.

- [ ] **Phase two:** Through a T+1 transfer, the platform moves money settled to it by the acquiring institution into the account it opened with the payout institution, in fixed amounts according to merchants’ withdrawal amounts. Merchants can then withdraw money from their platform balance accounts directly into their own accounts. To ensure merchants can withdraw quickly, the project uses prefunding: before the project operates, funds are advanced to the payout institution through a treasury account.

After the platform develops and matures, it will certainly add multiple acquiring institutions to introduce more payment instruments. When an acquirer does not support USD settlement, the platform needs an FX institution to convert other currencies to USD and settle them to the platform. The fund flow then becomes:

![](https://cdn.nlark.com/yuque/0/2026/png/719664/1767518918849-342aa652-3e86-4fbb-ac9c-4fd212fede98.png)

As the diagram shows, the platform must now recognize the user’s payment currency and complete its own rate lock and conversion from LCY to USD.

## Accounting capabilities — how a platform records money
Since money must move and be transferred N times from buyers to merchants, how do we ensure that it is recorded correctly? This requires understanding a platform’s accounting capability, namely how it records money. The platform creates N virtual accounts internally to represent flows among different accounts. Internet companies generally use double-entry bookkeeping; interested readers can explore it further. Here are several classic account types:

1. **Pending-association account**: after a buyer pays, funds are recorded in the pending-association account.
2. **Escrow account**: after the system associates the funds with an order, the merchandise-payment portion moves from the pending-association account to the escrow account.
3. **Revenue account**: the system moves the platform’s receivable portion (transaction service fees, processing fees, and so on) to the revenue account.
4. **Tax account**: the system moves taxes withheld and remitted for merchants (such as EPR and GST) to the tax account and reports them to the corresponding authorities on schedule.
5. **Merchant balance account**: after a merchant fulfills, money moves from the escrow account to the merchant balance account.
6. **Dedicated withdrawal account**: after a merchant initiates a withdrawal, money in the balance account moves to the dedicated withdrawal account.
7. **Refund transit account**: after a buyer requests a refund, funds are gathered into the refund transit account through fund preparation and paid to the payment channel.

Here is a classic flowchart (including forward and reverse flows) for a more detailed view:

![](https://cdn.jsdelivr.net/gh/wxxlamp/blog-img-repo@main/images/b01fb88d_b3430345.png)
