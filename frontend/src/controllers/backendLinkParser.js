import loadConfig from "../config";
import { feed, feedTracks } from "./localFeedStore.js";

export async function requestLinkedFeeds(url) {
  const config = await loadConfig();

  fetch(`${config.backendUrl}/link/feed?url=${encodeURIComponent(url)}`)
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

  let newFeed = [];
  let newFeedTracks = [];
  const valueObject = parseValue(response);

  for (const feedItem of feeds) {
    let feedObj = {
      type: "feed",
      artist: feedItem.artist,
      title: feedItem.title,
      description: feedItem.description,
      link: feedItem.link,
      image: feedItem.art_url,
    };
    newFeed.push(feedObj);

    for (const item of feedItem.items) {
      let track = {
        type: "track",
        title: item.title,
        artist: item.artist || feedItem.artist,
        description: item.description,
        audio: item.enclosure_url,
        image: item.image || feedItem.art_url,
        value: valueObject,
        transcript: item.transcript || "",
      };
      newFeedTracks.push(track);
    }
    feed.splice(0, feed.length, ...newFeed);
    feedTracks.splice(0, feedTracks.length, ...newFeedTracks);
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
        recipient: valueItem.Name || "None",
        valueType: valueItem.Type || "None",
        address: valueItem.Address || "None",
        customKey: valueItem.CustomKey || "None",
        customValue: valueItem.CustomValue || "None",
        split: valueItem.Split || "None",
      };
      valueObject.customRecord =
        valueObject.customKey && valueObject.customValue
          ? { [valueObject.customKey]: valueObject.customValue }
          : {};
      recipients.push(valueObject);
    }
  }
  return recipients;
}

function handleError(message) {
  console.log("Error encountered while reading response from backend.");
  console.log(message);
}
