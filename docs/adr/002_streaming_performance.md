# ADR 002: Quick Performance for Streaming & Data Retrieval
Status: Proposed

Date: October 3, 2025

## Context
RSS Feeds contain links to audio files, which are hosted on external servers. Retrieval
of this data quickly, is paramount to a good user experience. Our goal is to keep the
amount of resources required minimal, while the amount of data is the most possible,
while making data retrieval fast.

### Key Drivers
- **Quick Retrieval:** Decrease the time to play, retrieve, and load audio.
- **Consistent Data:** Ensure the data retrieved is consistent and secure.

## Non-Functional Requirements
- **Quick Streaming:** Streaming should start in 500 ms of track choosing.
- **Fast UI Parts:** User Interface Loads Quickly, within 300 ms of being changed.
- **Consistent Data:** Streaming tries to be uninterrupted once started.
- **Low Cost:** It should be cost-effective for us to permit all actions for free for
users.
- **Efficient:** Should use the least amount of resources as possible while maximizing
uptime.
- **Minimal Lag:** Users should deal with the least amount of time in between inputs.

## Options
**1. Frontend API Requests:** A completely fronted application where users make requests
to either the PodcastIndex or an individual feed.

Pros: efficient; quick uptime;

Cons: unscalable; barely usable; not different then pre-existing;

**2. Self-Hosted Backend (Chosen):** A backend hosted by ourselves seeded by the
PodcastIndex, where we make updates to our users feeds by polling the index.

Pros: consistent; reliable; authentic; efficient;

Cons: costly; harder implementation; larger storage space;

**3. Create Empty Database:** A backend hosted by ourselves, but the database is
completely empty and completely under our control.

Pros: total control; quick startup; small space needed;

Cons: non-enticing; empty until upload; no authenticity;

## Decision
We chose **Option 2** for our project for a number of reasons. Firstly, we believe that
the pre-existing data on the database is extremely important for a reliable user
experience. If users would have to upload pre-existing feeds just for other users to
use, it would also be inefficient, and difficult to track authenticity. We also believe
it is the fastest way for our users to receive data from our app, since with one, there
is no data in the database, there's none to be retrieved, and with a fronted, it will
simply be too difficult to effectively query the database at high volumes of traffic.
For these reasons we have chosen **Option 2.**

## Consequences

### Positive
- Data is consistent since we are able to both poll the podcast index API, and update
our own database with user uploaded tracks.
- Data Retrieval is quick, since we will have complete control over the routes, time to
execution for requests, and structure of the entire backend.
- Users are more likely to trust the application, since it will contain recognizable
tracks and podcasts on the application.

### Negative
- The amount of space and resources required to kickstart our backend is much larger.
- The difficulty of this implementation is much higher than others.

## Risks and Mitigations

- **Lag:** Streams drop packets or they take too long to arrive.

Focus on issues relating to lag, implementing multiple buffers to ensure data loss is
minimal.

- **Data Corruption:** Song glitches or breaks while streaming.

Require constant integrity checks on data retrieved, and if data is corrupted, make sure
the user is not seriously affected.

- **Request Loop:** App constantly tries to play song, when it just isn't available.

Make sure our database is consistently up-to-date with any changes to the index, and
have fail safes if user requested feeds contain songs where the audio isn't available.
