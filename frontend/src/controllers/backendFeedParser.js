import loadConfig from "../config";
import { searchedFeeds } from "./localFeedStore.js";
import { setLoading, setError, clearError } from "./statusStore.js";

export async function requestFeeds(query) {
  const config = await loadConfig();
  setLoading(true);

  try {
    const response = await fetch(
      `${config.backendUrl}/search/feeds?query=${encodeURIComponent(query)}&count=50`,
    );

    // Try to parse error response from backend
    const data = await response.json();

    if (!response.ok) {
      // Check for specific external API errors
      if (data.error === "ExternalApiBadResponse") {
        setError(
          "external-error",
          "PodcastIndex Error",
          "The PodcastIndex returned invalid data. Please try again later.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (data.error === "ExternalApiTimeout") {
        setError(
          "external-error",
          "Search Timeout",
          "The PodcastIndex is taking too long to respond. Please try again.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (data.error === "ExternalApiUnavaliable") {
        setError(
          "external-error",
          "Service Unavailable",
          "The PodcastIndex service is temporarily unavailable. Please try again later.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (response.status >= 500) {
        setError(
          "error",
          "Server Error",
          "Something went wrong on our end. Please try again.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (response.status >= 400) {
        setError(
          "error",
          "Invalid Request",
          "Your request was rejected by the server. Please try again.",
          "Retry",
          () => requestFeeds(query),
        );
      }
      return;
    }

    // Success case
    if (!data.feeds || data.feeds.length === 0) {
      setError(
        "empty-feed-error",
        "No Results",
        `No music feeds found matching "${query}".`,
        "Try Another Search",
        () => clearError(),
      );
    } else {
      clearError();
      parseResponse(data);
    }
  } catch {
    setError(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      () => requestFeeds(query),
    );
  } finally {
    setLoading(false);
  }
}

function parseResponse(response) {
  // console.log(response["feeds"]);
  Object.assign(searchedFeeds, response["feeds"]);
  searchedFeeds.splice(0, searchedFeeds.length, ...response["feeds"]);
}
