import loadConfig from "../config";
import { feed, feedTracks } from "./localFeedStore.js";
import { setLoading, setError, clearError } from "./statusStore.js";

export async function requestLinkedFeeds(url) {
  const config = await loadConfig();
  setLoading(true);

  try {
    const response = await fetch(
      `${config.backendUrl}/link/feed?url=${encodeURIComponent(url)}`,
    );

    // Try to parse error response from backend
    const data = await response.json();

    if (!response.ok) {
      // Check for specific error types
      if (
        data.error === "ExternalApiBadResponse" ||
        data.error === "InternalApiBadResponse"
      ) {
        setError(
          "feed-error",
          "Feed Parse Error",
          "Unable to read this RSS feed. The feed may have invalid syntax or be unreachable.",
          "Try Another",
          () => clearError(),
        );
      } else if (
        data.error === "ExternalApiTimeout" ||
        data.error === "InternalApiTimeout"
      ) {
        setError(
          "external-error",
          "Feed Timeout",
          "The feed took too long to load. Please try again.",
          "Retry",
          () => requestLinkedFeeds(url),
        );
      } else if (data.error === "ExternalApiUnavaliable") {
        setError(
          "external-error",
          "Service Unavailable",
          "The feed service is temporarily unavailable. Please try again later.",
          "Retry",
          () => requestLinkedFeeds(url),
        );
      } else if (response.status >= 500) {
        setError(
          "error",
          "Server Error",
          "Something went wrong on our end. Please try again.",
          "Retry",
          () => requestLinkedFeeds(url),
        );
      } else if (response.status >= 400) {
        setError(
          "error",
          "Invalid Request",
          "Your request was rejected by the server. Please try again.",
          "Retry",
          () => requestLinkedFeeds(url),
        );
      }
      return false;
    }

    clearError();
    parseResponse(data);
    return true;
  } catch {
    setError(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      () => requestLinkedFeeds(url),
    );
    return false;
  } finally {
    setLoading(false);
  }
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

    feedItem.items.forEach((item, index) => {
      let track = {
        type: "track",
        trackNumber: index + 1,
        title: item.title,
        artist: item.artist || feedItem.artist,
        description: item.description,
        audio: item.enclosure_url,
        image: item.image || feedItem.art_url,
        value: valueObject,
      };
      newFeedTracks.push(track);
    });
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
