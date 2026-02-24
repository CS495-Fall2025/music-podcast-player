import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  searchHistory,
  saveSearchHistory,
  loadSearchHistory,
  addSearch,
  clearSearchHistory,
  setSaveHistory,
} from "../src/controllers/searchHistory.js";

// Minimal cookie emulation so getCookie/setCookie work in tests
function resetCookies() {
  document.__cookieStore = "";
}

Object.defineProperty(document, "cookie", {
  get() {
    return document.__cookieStore || "";
  },
  set(val) {
    const [pair] = val.split(";"); // "name=value"
    const [name] = pair.split("=");

    const existing = (document.__cookieStore || "")
      .split("; ")
      .filter(Boolean)
      .filter((c) => !c.startsWith(name + "="));

    existing.push(pair.trim());
    document.__cookieStore = existing.join("; ");
  },
});

describe("searchHistory controller (minimum)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetCookies();
    searchHistory.value = [];
    saveSearchHistory.value = true;
  });

  it("adds queries to the front and removes duplicates", () => {
    addSearch("hello");
    addSearch("world");
    addSearch("hello"); // should move to the top, not duplicate

    expect(searchHistory.value).toEqual(["hello", "world"]);
  });

  it("caps history at 25 items", () => {
    for (let i = 0; i < 40; i++) addSearch("q" + i);

    expect(searchHistory.value.length).toBe(25);
    expect(searchHistory.value[0]).toBe("q39"); // most recent first
  });

  it("clearSearchHistory empties history", () => {
    addSearch("a");
    addSearch("b");

    clearSearchHistory();
    expect(searchHistory.value).toEqual([]);
  });

  it("disabling save history clears and prevents storing", () => {
    addSearch("a");
    setSaveHistory(false);

    expect(saveSearchHistory.value).toBe(false);
    expect(searchHistory.value).toEqual([]);

    addSearch("b");
    expect(searchHistory.value).toEqual([]); // still empty
  });

  it("loadSearchHistory does not crash on invalid JSON cookie", () => {
    // simulate cookies
    document.cookie = `saveSearchHistory=true`;
    document.cookie = `searchHistory=${encodeURIComponent("not-json")}`;

    loadSearchHistory();
    expect(searchHistory.value).toEqual([]);
  });
});
