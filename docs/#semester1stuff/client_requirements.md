# Requirements

## Functional

### Parse feed from user-provided URL
(1: Must-have)

A listener should have the ability to paste in a URL to a feed they want to listen to.
We should then fetch the feed, parse it, and display a list of tracks in that feed so
they can stream them.

### Search for feeds
(1: Must-have)

Listeners should be able to type in keywords to search the PodcastIndex's database of
music feeds. They should then be able to select one and view/stream the tracks in it.

### Music playback controls
(1: Must-have)

Listeners should have continuous playback, meaning when one track finishes, it should 
automatically stream the next. Additionally, users should have the ability to loop the
feed, loop the track, shuffle the feed, and skip tracks.

### Display track title, artist, album cover, and description
(1: Must-have)

When tracks are displayed in the app, they should include the title of the track, the
artist(s) that made the track, the album cover for the track, and the description of the
track. If the description is written in HTML, it should be displayed, such as for
linking to external sites.

### Boostagrams
(1: Must-have)

Listeners should be able to boost the artist they are currently listening to. This means
they should be able to connect a Bitcoin Lightning wallet, select an amount of sats, 
write a message, and have a keysend payment with Boost metadata sent to the track's 
value recipients' wallets according to the split specified by the feed.

### Sat dripping
(3: Could-have)

Listeners should be able to set an amount of sats per minute to automatically be paid to
whatever feed they are listening to when the minute lapses.

### About page
(3: Could-have)

There should be an about page that is easily editable by the client without him having
to rebuild the frontend.

### Remove tracks from current feed with a swipe
(3: Could-have)

Users should be able to identify and disable tracks in a feed they don't want to listen
to. (We believe a playlist feature could be better.)


## Nonfunctional

### Mobile friendly user interface

The user interface for the website should scale accordingly when on mobile and be easily
navigable. For instance, page navigation could move to the bottom of the screen so that
users can reach it easily.

### Minimal gaps in streaming

The app should avoid gaps in streaming longer than 500ms if possible.
