# ADR 004: Lightning Wallet for Podcasting 2.0 Music Feeds
Status: Accepted

Date: September 20, 2025

## Context
We want artists on our platform to be compensated directly using their Bitcoin Lightning
wallets within their feed. The system must integrate smoothly with our decentralized
music distribution approach while remaining cost-effective, secure, and user-friendly.

### Key Drivers

- **Direct artist payments:** Artists should receive funds instantly with minimal
intermediaries.
- **Low transaction cost:** Lightning payments provide near-zero fees compared to
traditional payment processors.
- **Decentralization:** Maintain artist ownership and avoid central custody of funds.
- **Global accessibility:** Support a payment mechanism that works across borders
without requiring bank integration.

## Non-Functional Requirements
- **Direct artist payments:** Artists should receive funds instantly with minimal
intermediaries.
- **Low transaction cost:** Lightning payments provide near-zero fees compared to
traditional payment processors.
- **Decentralization:** Maintain artist ownership and avoid central custody of funds.
- **Global accessibility:** Support a payment mechanism that works across borders
without requiring bank integration.

## Options
**1. Traditional Payment Processor (Stripe/PayPal, etc.)**

Pros: Well-documented, existing integrations, broad user familiarity.

Cons: High fees, limited global access, undermines decentralization goals.

**2. Direct Lightning Payment Links (User-sourced)**

Artists provide a Lightning address or LNURL directly in their feed. Clients parse and display a "tip"
button.

Pros: Simple, decentralized, low maintenance; no custody.

Cons: Inconsistent UX; clients must implement Lightning integration; limited
tracking/analytics.

**3. Bitcoin Connect Integration (Chosen)**

Use Bitcoin Connect, a JavaScript SDK that enables Lightning and on-chain Bitcoin payments via
wallet connection.

Pros: Consistent, standardized UX; abstracts wallet connection logic;
decentralized/non-custodial; integrates easily with feeds; strong developer support.

Cons: Dependency on a third-party SDK; requires clients to support wallet connection
flows

## Decision
We adopt **Option 3: Bitcoin Connect Integration.**

The client will:
- Use Bitcoin Connect to handle wallet discovery, connection, and payment requests.
- Parse artist Lightning payment identifiers (Lightning Address / LNURL) from feeds.
- Enable listeners to pay artists directly through their connected Lightning wallet.
- Keep the flow user-controlled, our platform does not hold or process funds.

## Consequences

### Positive
- Direct, instant, global payments to artists.
- Consistent user experience across browsers and devices.
- Maintains decentralization—artists fully control their wallets.
- Minimal operational overhead compared to building/maintaining a custom proxy

### Negative
- Platform is reliant on continued support and stability of Bitcoin Connect.
- Requires user onboarding for Lightning-enabled wallets.

## Risks and Mitigations
- **Dependency Risk:** Bitcoin Connect may change APIs or lose support.

Abstract integration layer; monitor upstream updates.

- **Compliance Risk:** Financial laws in different places might change.

Make it clear that we don't ever hold people's money, and check with legal experts if
needed.

- **Adoption Risk:** Not all listeners have Lightning-enabled wallets.

Provide clear onboarding and wallet recommendations
