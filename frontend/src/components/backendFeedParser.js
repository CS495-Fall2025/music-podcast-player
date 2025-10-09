import { searchedFeeds } from "./localFeedStore.js";

export function requestFeeds(query) {
  fetch(
    `http://localhost:5000/search/feeds?query=${encodeURIComponent(query)}&count=50`,
  )
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
  console.log(response["feeds"]);
  Object.assign(searchedFeeds, response["feeds"]);
  searchedFeeds.splice(0, searchedFeeds.length, ...response["feeds"]);
}

function handleError(message) {
  console.log("Error encountered while reading response from backend.");
  console.log(message);
}
