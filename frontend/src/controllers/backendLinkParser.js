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
    .catch((error) => {
      handleError(error.message);
    });
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
  const valueObject = parseValue(response);

  for (const feedItem of feeds) {
    let album = {
      type: "album",
      artist: feedItem.artist,
      title: feedItem.title,
      description: feedItem.description,
      link: feedItem.link,
      image: feedItem.art_url,
      value: valueObject
    };
    newAlbum.push(album);
    for (const item of feedItem.items) {
      let track = {
        type: "track",
        title: item.title,
        artist: item.artist || feedItem.artist,
        description: item.description,
        audio: item.enclosure_url,
        image: item.image || feedItem.art_url,
      };
      newFeed.push(track);
      console.log(track);
    }
    feed.splice(0, feed.length, ...newFeed);
  }
}

function parseValue(response) {
  const feeds =
    response.feeds ??
    (response.feed
      ? Array.isArray(response.feed)
        ? response.feed
        : [response.feed]
      : null);

  const recipients = [];

  for (const feedItem of feeds) {
    for (const valueItem of feedItem.value_items) {
      let valueObject = {
        type: "value",
        recipient: valueItem.recipientName || "None",
        valueType: valueItem.type || "None",
        address: valueItem.recipientAddress || "None",
        customKey: valueItem.recipientCustomKey || "None",
        customValue: valueItem.recipientCustomValue || "None",
        split: valueItem.recipientSplit || "None",
      };
      valueObject.customRecord =
        valueObject.customKey && valueObject.customValue
          ? { [valueObject.customKey]: valueObject.customValue }
          : {};
      recipients.push(valueObject);
      console.log(valueObject);
    }
  }
  return recipients;
}

function handleError(message) {
  console.log("Error encountered while reading response from backend.");
  console.log(message);
}
