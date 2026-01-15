import { feed } from "./localFeedStore.js";

export function requestLinkedFeeds(url) {
  fetch(`http://localhost:5000/link/feed?url=${encodeURIComponent(url)}`)
    .then((response) => {
      if (!response.ok) {
        console.log(`Request returned status ${response.status}`);
        throw new Error(`Request returned status ${response.status}`);
      }
      return response.json();
    })
    .then((response) => parseResponse(response))
    .catch((message) => handleError(message));
}

function parseResponse(response) {
  const feeds =
    response.feeds ??
    (response.feed
      ? Array.isArray(response.feed)
        ? response.feed
        : [response.feed]
      : null);

  let newAlbum = [];
  let newFeed = [];

  for (const feedItem of feeds) {
    let albumObject = {
      type: "album",
      artist: feedItem.artist,
      title: feedItem.title,
      description: feedItem.description,
      link: feedItem.link,
      art_url: feedItem.art_url,
    };
    newAlbum.push(albumObject);
    for (const item of feedItem.items) {
      let trackObject = {
        type: "track",
        title: item.title,
        description: item.description,
        audio: item.enclosure_url,
        image: item.image,
      };
      newFeed.push(trackObject);
    }
  }
  feed.splice(0, feed.length, ...newFeed);
  console.log(newAlbum);
  console.log(newFeed);
}

function handleError(message) {
  console.log("Error encountered while reading response from backend.");
  console.log(message);
}
