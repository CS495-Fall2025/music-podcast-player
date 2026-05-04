# ADR 003: RSS Feed Fetching
Status: Superseeded (by option 3)

Date: October 3, 2025

## Context
In order to provide our users with updated access to various artists RSS feeds, we need
to have a system for fetching these feeds from the external servers where they are
hosted. These feeds will then need to be parsed into a format that our web application
can understand.

### Key Drivers
- **Recency:** Feeds and the data dependent on them should be kept up to date
particularly when viewed by the user.
- **Reliability:** The feed parser and fetching system must be able to handle servers
that are unavailable, incorrect or malicious data, or large amounts of valid data while
communicating the state of the application clearly to the user and remaining in a known
state.
- **Intuitive:** The interface for finding feeds should be intuitive for the average
user and not require a deep knowledge of RSS.

## Non-Functional Requirements
- **Cost:** The application should be able to be run cheaply at least in its initial
phase. This means considering using reactionary APIs with cold starts and static
hosting. The application should still function well even with these constraints. This
means the application cannot rely on background processing.
- **Consistent with Podcasting 2.0:** Any tags that are part of Podcasting 2.0 should at
least be allowed in the feeds received by the RSS parser. Any extraneous tags can be
ignored. Similarly, the parser should not depend on tags outside this standard.
- **Respectful of Ownership:** The application should not import feeds that are tagged
as locked without verifying the identity of the person importing the feed. Similarly,
the application should convey ownership of a feed to someone without verifying
ownership. Additionally, the application should respect the value tag on feeds and allow
users to make value-for-value payments according to the split indicated on the tag.
- **Performance and Efficiency:** The application should not take more than 500ms to
process an RSS feed and should avoid reprocessing feeds it has recently processed unless
it expects they have changed.
- **Respectful of Hosting Servers and the PodcastIndex:** The application should not
make more than one request to the PodcastIndex API per second to avoid rate-limiting and
abuse of the API. Similarly, requests to external servers hosting RSS feeds should be at
least a minute apart, and caching should be used in between.

## Options
**1. Parsing exclusively on the frontend:** We could receive and parse RSS feeds
exclusively on the frontend. This would allow us to just do static hosting and allows
parsing to be distributed among users. The downsides are that we cannot really do
caching, share parsed results between users, or allow users to find feeds that they
don't already have a URL for. Additionally, since the PodcastIndex's API is
authenticated, we would not be able to use that. We would also run into CORS issues from
trying to load feeds from cross-site sources and would have to use a proxy.
**2. Provide feeds from the backend and parse them in the frontend:** Compared to the
previous option, this would allow us to have feed search features though the
PodcastIndex API and keep a shared store of feeds should we choose, limiting the load on
their server. The downsides are we cannot share feed-parsing results between users and
so our caching would be limited to feed discovery, not feed pulling. Additionally, users
would only view pre-made feeds by artists, and wouldn't be able to have features like
favorite tracks, recommendations, or playlists. Since these feed's value tags are parsed
on the frontend, we'd run the risk of a virus on a user's computer modifying the request
to send money.
**3. Parsing is handled on the backend, but feeds are not stored:** This would allow us
to have only a frontend and backend, and, compared to previous options, still have some
capacity to cache feed parsing results. However, it would require many requests to the
PodcastIndex from our backend, and we could get rate-limited or blocked. Additionally,
we'd only really be able to cache a limited number of popular tracks, so users would
have limited performance on playlists using other tracks.
**4. Parsing is handled by the backend, and track information is saved:** This option
allows us to easily rate-limit our requests to the PodcastIndex, as we could even handle
searching ourselves, we'd only need to request the list of music feeds every hour to
stay updated. Additionally, we'd be able to store information on all the tracks inside
each feed, as well as be able to accept unlocked feeds from users and locked feeds from
artists who we've confirmed own the feed. This option is the best for user features and
independence from external APIs, but requires a database in addition to our frontend and
backend, and is therefore the most complicated to set up and host.

## Decision
We've decided to implement **Option 4: Parsing is handled by the backend, and track
information is saved.** This entails writing a class/module on the backend that handles
parsing of an RSS feed. Additionally, the backend will keep track of when feeds were
last updated, as well as a separate database table for tracks inside those feeds, so
users can find them individually. Users will be able to send search queries to our
backend using the `/search` endpoint. Also, users will be able to add an RSS feed that
the application doesn't already index using a `POST` request to the `/feeds` endpoint.
If a user is just browsing tracks we've already indexed, then no additional parsing is
necessary, except in the case where a feed has not been fetched and updated within the
last two hours. Feeds will only update when their data is requested, at least for now.

## Consequences

### Positive
We will be able to fetch feeds without the use of a CORS proxy. We will also be able to
store the results of parsing, which will dramatically lower the number of requests our
backend needs to make to external services and increase its independence. Since we are
making these requests on our backend, we can use the PodcastIndex as a source for new
RSS feeds using their `/podcasts/bymedium` and `/static/tracking/current` to get new
music feeds that have been added over the past 24 hours. Additionally, since we do not
strictly depend on the PodcastIndex's data, we can allow users and artists to add feeds
we don't already have to our site. We can also more easily protect the user from
malicious feeds by parsing them server side.

### Negative
The downsides to this approach are mainly that it requires a more complicated setup (a
backend and database) and requires a stronger design for security, user data, and
managing resource usage. Additionally, since we aren't updating feeds every time a user
requests them, they may be more out of date. (Though, if a feed has temporarily gone
offline, our backend can handle that but our frontend cannot.) It will also be harder to
convince our client that this is a wiser approach than handling everything in the
frontend.

## Risks and Mitigations
- **Attacks on backend:** By choosing to parse feeds on our backend, we are a greater
target than a random user using our frontend, as a successful attack could damage our
app, bring it offline or, in a worst-case scenario, result in stolen user data.

We can mitigate this risk by storing data securely (hashing and salting passwords for
instance), as well as including thorough integration tests that test the application's
response to malicious feeds.

- **Resource limitations:** Since our backend will need to be making calls to both RSS
feed servers and the PodcastIndex API, we need to ensure we do not exceed limitations
on network usage and memory imposed by our hosting plan (likely free). Additionally, we
need to avoid spamming hosting services and the PodcastIndex with requests, as we risk
being blocked.

To mitigate this, we can enforce rate limits per hosting provider and the PodcastIndex.
Additionally, caching data we've already parsed recently as well as fetching feeds in
groups should reduce our network usage.

- **Availability:** Since our app will include a backend and database, it will only
function when these components are online. If one were to fail, our whole application
would be offline. We could mitigate this by allowing users to store references to
certain tracks in a browser cookie, allowing them to listen even if only the frontend is
online.
