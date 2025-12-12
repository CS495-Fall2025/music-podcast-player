# ADR 005: Recommendation Feature for Listeners
Status: Proposed

Date: October 3, 2025

## Context
We are building a music distribution and playback app that consumes artists' RSS feeds
using the Podcasting 2.0 `podcast:music` tag family and related tools. We want the user
to be given content recommendations that are tailored to them based on the content they
have listened to in the past.

### Key Drivers
- **Personalization:** Present content based on listening history or artist/genre
similarity.
- **Discovery:** Present suggestions that may be out of the user's comfort zone, but is
similar enough to their preferences.
- **Privacy:** User listening data should be kept secure.

## Non-Functional Requirements
- **Performance:** Recommendations should be generated quickly, &lt;500ms.
- **Relevance:** The recommendations must be related to the content that the user has
subscribed to and listened to frequently.
- **Adaptability:** Content should change if user's taste changes.
- **Scalability:** Must support a large number of users simultaneously.
- **Data Privacy:** Collect as little information as possible.

## Options
**1. Rules Based System:** Recommend content based on what user listens to the most,
based on tags/genres from the RSS data.

Pros: Quick implementation.

Cons: Shallow system, will not scale with varied listening habits.

**2. Content Based Filtering:** Use metadata from RSS feeds(genres, keywords, artists)

Pros: Works well with RSS feed data.

Cons: Could reduce content diversity.

**3. Collaborative Filtering:** Use aggregated listening patterns to recommend similar
users' interests.

Pros: Much more personalization, better discoverability.

Cons: Requires large database and much more data collection, will take a while to build.

## Decision
We will go with **Option 2: Content Based Filtering** for our recommendation system.
- A simple backend database will store minimal metadata about users' listening habits.
- This metadata will be used to search for and display content similar to what the user
enjoys.
- Cache most common content tags to improve performance.

## Consequences

### Positive
- Works well with RSS feeds.
- Users will see content similar to that which they enjoy.
- Won't be a resource heavy system.

### Negative
- May reduce content diversity.
- New users will not be given much since there will be no data associated with them.

## Risks and Mitigations
- **Poor tagging (Risk):** Improper tagging by the feed owner could reduce
recommendation accuracy.

Use general popularity to present recommendations.

- **Lack of diversity (Risk):** Users may not get different enough recommendations.

Blend in some content from unrelated genres.

- **Privacy and Security (Risk):** Even minimal data could be leaked.

Encrypt any user data that is stored and implement strict access control.
