import { describe, it, expect } from "vitest";
import {
  feed,
  currentTrack,
  searchedFeeds,
} from "../src/controllers/localFeedStore.js";

describe("localFeedStore", () => {
  // Test feed array initialization
  it("feed is initialized as an empty reactive array", () => {
    expect(Array.isArray(feed)).toBe(true);
    expect(feed.length).toBe(0);
  });

  // Test currentTrack ref initialization
  it("currentTrack is initialized as an empty ref string", () => {
    expect(currentTrack.value).toBe("");
  });

  // Test searchedFeeds array initialization
  it("searchedFeeds is initialized as an empty reactive array", () => {
    expect(Array.isArray(searchedFeeds)).toBe(true);
    expect(searchedFeeds.length).toBe(0);
  });

  // Test feed array mutability
  it("feed can be modified", () => {
    const testItem = {
      type: "audio",
      title: "Test",
      imageUrl: "test.jpg",
      audioUrl: "test.mp3",
    };
    feed.push(testItem);
    expect(feed[0]).toEqual(testItem);
    feed.splice(0, feed.length);
  });

  // Test currentTrack ref mutability
  it("currentTrack can be modified", () => {
    const testUrl = "http://test.com/audio.mp3";
    currentTrack.value = testUrl;
    expect(currentTrack.value).toBe(testUrl);
    currentTrack.value = "";
  });

  // Test searchedFeeds array mutability
  it("searchedFeeds can be modified", () => {
    const testFeed = { id: 1, title: "Test Feed" };
    searchedFeeds.push(testFeed);
    expect(searchedFeeds[0]).toEqual(testFeed);
    searchedFeeds.splice(0, searchedFeeds.length);
  });
});
