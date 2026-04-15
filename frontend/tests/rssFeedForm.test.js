import { describe, it, expect, vi, beforeEach } from "vitest";
import router from "../src/router";

vi.mock("../src/router", () => ({
  default: {
    push: vi.fn(),
  },
}));

vi.mock("../src/controllers/backendLinkParser.js", () => ({
  requestLinkedFeeds: vi.fn(),
}));

describe("rssFeedForm controller", () => {
  let canSubmit,
    onUserFeedInputBlur,
    onUserFeedInputInput,
    onUserFeedFormSubmit;
  let requestLinkedFeeds;

  // Import fresh modules and reset state before each test
  beforeEach(async () => {
    vi.clearAllMocks();
    vi.resetModules();

    const formModule = await import("../src/controllers/rssFeedForm.js");
    const parsingModule = await import(
      "../src/controllers/backendLinkParser.js"
    );

    canSubmit = formModule.canSubmit;
    onUserFeedInputBlur = formModule.onUserFeedInputBlur;
    onUserFeedInputInput = formModule.onUserFeedInputInput;
    onUserFeedFormSubmit = formModule.onUserFeedFormSubmit;
    requestLinkedFeeds = parsingModule.requestLinkedFeeds;
  });

  describe("URL validation", () => {
    // Test validation accepts http protocol
    it("accepts valid http URLs", () => {
      const event = {
        target: { value: "http://example.com/feed" },
      };

      onUserFeedInputInput({ target: { value: "invalid" } });
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });

    // Test validation accepts https protocol
    it("accepts valid https URLs", () => {
      const event = {
        target: { value: "https://example.com/feed" },
      };

      onUserFeedInputInput({ target: { value: "invalid" } });
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });

    // Test validation rejects malformed URLs
    it("rejects invalid URLs", () => {
      const event = {
        target: { value: "not-a-url" },
      };

      onUserFeedInputBlur(event);

      expect(canSubmit.value).toBe(false);
    });
  });

  describe("form submission", () => {
    // Test preventDefault is called on form submit
    it("prevents default form submission", () => {
      const preventDefault = vi.fn();
      const formData = new Map([["userFeedUrl", "https://example.com/feed"]]);

      const event = {
        preventDefault,
        target: {
          reset: vi.fn(),
        },
      };

      globalThis.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      onUserFeedFormSubmit(event);
      expect(preventDefault).toHaveBeenCalled();
    });

    // Test successful form submission with valid URL
    it("submits form with valid URL", async () => {
      const url = "https://example.com/feed";
      const formData = new Map([["userFeedUrl", url]]);

      const event = {
        preventDefault: vi.fn(),
        target: {
          reset: vi.fn(),
        },
      };

      globalThis.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      requestLinkedFeeds.mockResolvedValueOnce(true);
      await onUserFeedFormSubmit(event);

      expect(event.target.reset).toHaveBeenCalled();
      expect(requestLinkedFeeds).toHaveBeenCalledWith(url);
      expect(router.push).toHaveBeenCalledWith("/view");
    });

    // Test form submission is blocked with invalid URL
    it("does not submit form with invalid URL", () => {
      const url = "not-a-url";
      const formData = new Map([["userFeedUrl", url]]);

      const event = {
        preventDefault: vi.fn(),
        target: {
          reset: vi.fn(),
        },
      };

      globalThis.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      onUserFeedFormSubmit(event);

      expect(event.target.reset).not.toHaveBeenCalled();
      expect(requestLinkedFeeds).not.toHaveBeenCalled();
      expect(router.push).not.toHaveBeenCalled();
    });
  });

  describe("input events", () => {
    // Test blur event triggers validation
    it("validates on blur", () => {
      const invalidEvent = {
        target: { value: "not-a-url" },
      };
      onUserFeedInputInput(invalidEvent);

      const validEvent = {
        target: { value: "https://example.com/feed" },
      };
      onUserFeedInputBlur(validEvent);

      expect(canSubmit.value).toBe(true);
    });

    // Test input event triggers validation
    it("validates on input", () => {
      onUserFeedInputInput({
        target: { value: "invalid" },
      });

      const event = {
        target: { value: "https://example.com/feed" },
      };
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });
  });
});
