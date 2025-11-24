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
  console.log(feeds);

  let newFeed = [];

  for (const feedItem of feeds) {
    let trackObject = {
      type: "track",
      title: feedItem.title ?? "No title",
      image: feedItem.image ?? null,
      audio: feedItem.enclosure?.url ?? null,
    };

    if (!trackObject.audio) {
      return;
    }
    newFeed.push(trackObject);
  }
  feed.splice(0, feed.length, ...newFeed);
  console.log(newFeed);
}

function handleError(message) {
  console.log("Error encountered while reading response from backend.");
  console.log(message);
}
