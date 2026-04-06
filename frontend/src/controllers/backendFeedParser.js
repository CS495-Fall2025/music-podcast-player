import loadConfig from "../config";
import { searchedFeeds } from "./localFeedStore.js";
import { setLoading, navigateToError, clearError } from "./statusStore.js";
import router from "../router";

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
        navigateToError(
          "external-error",
          "PodcastIndex Error",
          "The PodcastIndex returned invalid data. Please try again later.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (data.error === "ExternalApiTimeout") {
        navigateToError(
          "external-error",
          "Search Timeout",
          "The PodcastIndex is taking too long to respond. Please try again.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (data.error === "ExternalApiUnavaliable") {
        navigateToError(
          "external-error",
          "Service Unavailable",
          "The PodcastIndex service is temporarily unavailable. Please try again later.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (response.status >= 500) {
        navigateToError(
          "error",
          "Server Error",
          "Something went wrong on our end. Please try again.",
          "Retry",
          () => requestFeeds(query),
        );
      } else if (response.status >= 400) {
        navigateToError(
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
      navigateToError(
        "empty-feed-error",
        "No Results",
        `No music feeds found matching "${query}".`,
        "Try Different Search",
        () => router.push("/search"),
      );
    } else {
      clearError();
      parseResponse(data);
    }
  } catch {
    navigateToError(
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
  console.log(response["feeds"]);
  Object.assign(searchedFeeds, response["feeds"]);
  searchedFeeds.splice(0, searchedFeeds.length, ...response["feeds"]);
}
