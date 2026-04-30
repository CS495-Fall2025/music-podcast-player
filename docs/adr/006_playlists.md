# ADR 006: Playlists
Status: Accepted

Date: September 30, 2025

## Context
We believe users will want the ability to save and access playlists and favorite tracks
across multiple devices. A consistent and reliable storage system is essential to ensure
that user preferences follow them whether they log in on a phone, laptop, or tablet.

## Non-Functional Requirements
- **Reliability:** Data must be preserved without corruption or loss.
- **Availability:** Playlists should be accessible across devices with small downtime.
- **Performance:** The sync operations for this should feel seamless with updates that
are reflected in under 2 seconds.
- **Security:** User data must be stored securely with access controls and encryption.
- **Cost-effectiveness:** The system should be affordable to operate at scale.

## Options
**1. Local Device Storage**

Pros: Simple implementation, no recurring infrastructure cost, and it works offline.

Cons: Data does not sync across devices and has a high risk of loss if the device is
replaced or reset.

**2. Cloud Storage with an External Provider**

Pros: Scalable, secure, easy multi-device access, and built-in availability features.

Cons: Ongoing operational costs, dependency on third-party provider, and potential
vendor lock-in.

**3. Custom Backend with Database (Maybe MySQL)**

Pros: Full control over data model for future features like sharing and recommendations
and fine-tuned access controls.

Cons: The higher development and maintenance effort requires dedicated hosting and
monitoring.

## Decision
For our decision we will be using **Option 2** which is **Cloud Storage with External
Provider** since it offers the best balance between scalability, reliability, and ease
of implementation. By having managed services, we can minimize the initial development
overhead while making sure that the playlists remain accessible and consistent across
all devices.

## Consequences

### Positive
- There would be seamless cross-device syncing.
- There would be a reduced maintenance burden compared to self-hosted solutions.
- We would also have built-in scalability to handle growing user bases.

### Negative
- There would be recurring operational costs for this.
- There are some potential dependencies on the provider's uptime and pricing model.

## Risks and Mitigations
- **Vendor Lock-In:**

This can be mitigated by designing APIs with abstraction layers to allow migration if it
is needed.

- **Downtime:**

Downtime can be mitigated by enabling local caching and sync-on-reconnect features.

- **Cost Overruns:** Here we can mitigate by setting quotas, optimizing storage usage,
and monitoring provider pricing.
