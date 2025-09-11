import { feed } from "./localFeedStore.js";

// Note: THIS WILL NEED TO BE CHANGED FOR PRODUCTION. Currently we can use a CORS proxy
// to successfully fetch RSS feeds without the appropriate CORS headers, this is a
// temporary solution. The better (production-ready) solution is to use a backend.

export function requestFeedFromURL(url) {
  fetch(`https://corsproxy.io/?url=${url}`)
    .then((response) => {
      if (!response.ok) {
        console.log(`Request returned status ${response.status}`);
        return;
      }

      return response.text();
    })
    .then((rssFeed) => parseResponse(rssFeed))
    .catch((message) => handleError(message));
}

function parseResponse(rssRaw) {
  let newFeed = [];

  const parser = new DOMParser();
  const rss = parser.parseFromString(rssRaw, "text/xml");
  const channel = rss.querySelector("channel");

  const items = channel.querySelectorAll("item");
  const overallImageElement = channel.querySelector("image");
  const overallImage = overallImageElement
    ? overallImageElement.attributes.href.textContent
    : null;

  for (const item of items) {
    let trackObject = {
      type: "track",
    };

    trackObject.title = item.querySelector("title").textContent;

    const imageElement = item.querySelector("image");
    const image = imageElement
      ? imageElement.attributes.href.textContent
      : null;

    if (image) {
      trackObject.image = image;
    } else if (overallImage) {
      trackObject.image = overallImage;
    } else {
      trackObject.image = null;
    }

    const linkType =
      item.querySelector("enclosure").attributes.type.textContent;

    // If we don't have a link to the track's audio, don't bother showing it.
    if (!linkType.startsWith("audio")) {
      return;
    }

    trackObject.audio =
      item.querySelector("enclosure").attributes.url.textContent;

    newFeed.push(trackObject);
  }

  console.log(newFeed);
  Object.assign(feed, newFeed);
}

function handleError(message) {
  console.log("Error encountered while parsing RSS feed.");
  console.log(message);
}
