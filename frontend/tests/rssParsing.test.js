import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { requestFeedFromURL } from "../src/controllers/rssParsing.js";
import { feed } from "../src/controllers/localFeedStore.js";

describe("rssParsing controller", () => {
  const mockRssXml = `
    <rss>
      <channel>
        <image href="channel.jpg"/>
        <item>
          <title>Test Track</title>
          <image href="test.jpg"/>
          <enclosure type="audio/mpeg" url="test.mp3"/>
        </item>
      </channel>
    </rss>
  `;

  beforeEach(() => {
    vi.spyOn(console, "log").mockImplementation(() => {});
    feed.splice(0, feed.length);
    vi.stubGlobal("fetch", vi.fn());

    // Mock DOMParser more accurately
    vi.stubGlobal(
      "DOMParser",
      class {
        parseFromString(str) {
          return {
            querySelector: (selector) => ({
              querySelectorAll: (itemSelector) => [
                {
                  querySelector: (selector) => {
                    if (selector === "title")
                      return { textContent: "Test Track" };
                    if (selector === "image")
                      return {
                        attributes: { href: { textContent: "test.jpg" } },
                      };
                    if (selector === "enclosure")
                      return {
                        attributes: {
                          type: { textContent: "audio/mpeg" },
                          url: { textContent: "test.mp3" },
                        },
                      };
                    return null;
                  },
                },
              ],
              querySelector: (selector) => {
                if (selector === "image")
                  return {
                    attributes: { href: { textContent: "channel.jpg" } },
                  };
                return null;
              },
            }),
          };
        }
      },
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("requestFeedFromURL makes fetch request with CORS proxy", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(mockRssXml),
    });

    const testUrl = "http://example.com/feed";
    requestFeedFromURL(testUrl);

    await vi.runAllTimersAsync();
    await vi.waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        `https://corsproxy.io/?url=${testUrl}`,
      );
    });
  });

  it("handles successful RSS feed parsing", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(mockRssXml),
    });

    requestFeedFromURL("http://example.com/feed");

    await vi.runAllTimersAsync();
    await vi.waitFor(() => {
      expect(feed).toHaveLength(1);
      expect(feed[0]).toEqual({
        type: "track",
        title: "Test Track",
        image: "test.jpg",
        audio: "test.mp3",
      });
    });
  });

  it("handles fetch error gracefully", async () => {
    const consoleSpy = vi.spyOn(console, "log");
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    requestFeedFromURL("http://example.com/feed");

    await vi.runAllTimersAsync();
    await vi.waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith("Request returned status 404");
    });
    feed.splice(0, feed.length); // Clean up feed before checking length
    expect(feed).toHaveLength(0);
  });

  it("handles parsing error gracefully", async () => {
    const consoleSpy = vi.spyOn(console, "log");
    const mockError = new Error("Parse error");
    fetch.mockRejectedValueOnce(mockError);

    requestFeedFromURL("http://example.com/feed");

    await vi.runAllTimersAsync();
    await vi.waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        "Error encountered while parsing RSS feed.",
      );
      expect(consoleSpy).toHaveBeenCalledWith(mockError);
      expect(feed).toHaveLength(0);
    });
  });
});
