# Database Model Desription 
This document describes the data model for the RSS Music Player application. It serves as a written explanation of the ER/UML diagrams and defines the purpose of each entity and the relationships between them.

## users
Stores information about application users who can create playlists and save feeds.

- id INTEGER PRIMARY KEY  
- username VARCHAR NOT NULL UNIQUE  
- password VARCHAR NOT NULL  
- description VARCHAR  
- wallet_status BOOLEAN NOT NULL  
- saved_feeds INTEGER NOT NULL  
- created_at TIMESTAMP NOT NULL  

---

## creators
Here this represents content creators who publish RSS feeds and receive value-for-value payments.

- id INTEGER PRIMARY KEY  
- username VARCHAR NOT NULL UNIQUE  
- wallet_address VARCHAR NOT NULL  
- password VARCHAR NOT NULL  
- description VARCHAR  
- follow_count INTEGER NOT NULL  
- created_feeds INTEGER NOT NULL  
- created_at TIMESTAMP NOT NULL  

---

## feeds
Feeds represent RSS feeds created by creators that contain audio tracks.

- guid VARCHAR PRIMARY KEY  
- creator_id INTEGER KEY -> creators.id  
- url VARCHAR NOT NULL  
- description VARCHAR  
- category VARCHAR  
- track_count INTEGER NOT NULL  
- value_recipient VARCHAR NOT NULL  
- publish_date TIMESTAMP  

---

## tracks
Tracks represents individual audio tracks or podcast episodes within a feed.

- guid VARCHAR PRIMARY KEY  
- title VARCHAR NOT NULL  
- description VARCHAR  
- duration INTEGER NOT NULL (in seconds)  
- category VARCHAR  

---

## playlists
Playlists represents user-created collections of tracks.

- id INTEGER PRIMARY KEY
- title VARCHAR NOT NULL
- description VARCHAR
- track_count INTEGER NOT NULL DEFAULT 0
- created_by_user_id INTEGER FOREIGN KEY -> users.id
- created_at TIMESTAMP NOT NULL

---

## playlist_tracks
Here is a junction table that connects playlists and tracks, enabling a many-to-many relationship.

- id INTEGER PRIMARY KEY  
- playlist_id INTEGER KEY -> playlists.id  
- track_guid VARCHAR KEY -> tracks.guid  
- UNIQUE (playlist_id, track_guid)  

---

## feed_tracks
This is junction table that connects feeds and tracks, enabling the feeds to contain multiple tracks.

- id INTEGER PRIMARY KEY  
- feed_guid VARCHAR KEY -> feeds.guid  
- track_guid VARCHAR KEY -> tracks.guid  
- UNIQUE (feed_guid, track_guid)  

---
