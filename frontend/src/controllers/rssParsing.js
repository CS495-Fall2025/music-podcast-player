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

function resolveNamespace(prefix) {
	switch (prefix) {
		case "podcast":
			return "https://podcastindex.org/namespace/1.0";
		default:
			return null;
	}
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

	const overallValueElement = rss.evaluate(
		"podcast:value",
		channel,
		resolveNamespace,
		XPathResult.FIRST_ORDERED_NODE_TYPE,
		null
	).singleNodeValue;
	const overallValueData = parseValue(rss, overallValueElement);

	const feedGuidElement = rss.evaluate(
		"podcast:guid",
		channel,
		resolveNamespace,
		XPathResult.FIRST_ORDERED_NODE_TYPE,
		null
	).singleNodeValue;
	const feedGuid = feedGuidElement ? feedGuidElement.textContent : null;

	const feedTitleElement = channel.querySelector("title");
	const feedTitle = feedTitleElement.textContent;

  for (const item of items) {
    const trackObject = {
      type: "track",
			feedTitle: feedTitle,
    };

    trackObject.title = item.querySelector("title").textContent;

    const imageElement = item.querySelector("image");
    const image = imageElement
      ? imageElement.attributes.href.textContent
      : null;
	
		const valueElement = rss.evaluate(
			"podcast:value",
			item,
			resolveNamespace,
			XPathResult.FIRST_ORDERED_NODE_TYPE,
			null
		).singleNodeValue;
		const valueData = parseValue(rss, valueElement);
	
		const trackGuidElement = item.querySelector("guid");
		const trackGuid = trackGuidElement ? trackGuidElement.textContent : null;

    if (image) {
      trackObject.image = image;
    } else if (overallImage) {
      trackObject.image = overallImage;
    } else {
      trackObject.image = null;
    }

		if (valueData) {
			trackObject.value = valueData;
		} else if (overallValueData) {
			trackObject.value = overallValueData;
		} else {
			trackObject.value = [];
		}
		
		if (feedGuid) {
			trackObject.feedGuid = feedGuid;
		}
		if (trackGuid) {
			trackObject.guid = trackGuid;
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
  feed.splice(0, feed.length, ...newFeed);
}

// [{name, address, split, customRecord: {customKey: customValue}}]
function parseValue(rss, valueTag) {
	if (!valueTag) {
		return [];
	}

	const type = valueTag.getAttribute("type");
	const method = valueTag.getAttribute("method");

	if (type !== "lightning" || method !== "keysend") {
		return [];
	}

	const recipientElements = rss.evaluate(
		"podcast:valueRecipient",
		valueTag,
		resolveNamespace,
		XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
		null
	);

	const recipients = [];

	for (let i = 0; i < recipientElements.snapshotLength; i++) {
		const recipientElement = recipientElements.snapshotItem(i);
		
		const name = recipientElement.getAttribute("name") ?? "Unnamed Recipient";
		const type = recipientElement.getAttribute("type");
		const address = recipientElement.getAttribute("address");
		const split = recipientElement.getAttribute("split");
		const customKey = recipientElement.getAttribute("customKey");
		const customValue = recipientElement.getAttribute("customValue");

		if (type !== "node") {
			continue;
		}

		const recipientData = {
			name: name,
			address: address,
			split: split,
		};

		recipientData.customRecord = customKey && customValue
			? { [customKey]: customValue }
			: {};

		recipients.push(recipientData);
	}

	return recipients;
}

function handleError(message) {
  console.log("Error encountered while parsing RSS feed.");
  console.log(message);
}
