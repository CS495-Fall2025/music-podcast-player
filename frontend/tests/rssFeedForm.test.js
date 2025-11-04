import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import router from "../src/router";

vi.mock("../src/router", () => ({
  default: {
    push: vi.fn(),
  },
}));

vi.mock("../src/controllers/rssParsing.js", () => ({
  requestFeedFromURL: vi.fn(),
}));

describe("rssFeedForm controller", () => {
  let canSubmit,
    onUserFeedInputBlur,
    onUserFeedInputInput,
    onUserFeedFormSubmit;
  let requestFeedFromURL;

  beforeEach(async () => {
    vi.clearAllMocks();
    vi.resetModules();

    // Import fresh modules for each test to reset state
    const formModule = await import("../src/controllers/rssFeedForm.js");
    const parsingModule = await import("../src/controllers/rssParsing.js");

    canSubmit = formModule.canSubmit;
    onUserFeedInputBlur = formModule.onUserFeedInputBlur;
    onUserFeedInputInput = formModule.onUserFeedInputInput;
    onUserFeedFormSubmit = formModule.onUserFeedFormSubmit;
    requestFeedFromURL = parsingModule.requestFeedFromURL;
  });

  describe("URL validation", () => {
    it("accepts valid http URLs", () => {
      const event = {
        target: { value: "http://example.com/feed" },
      };

      // First make canSubmit false by entering invalid input
      onUserFeedInputInput({ target: { value: "invalid" } });
      // Then enter valid input
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });

    it("accepts valid https URLs", () => {
      const event = {
        target: { value: "https://example.com/feed" },
      };

      // First make canSubmit false by entering invalid input
      onUserFeedInputInput({ target: { value: "invalid" } });
      // Then enter valid input
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });

    it("rejects invalid URLs", () => {
      const event = {
        target: { value: "not-a-url" },
      };

      // Use blur to trigger validation (blur validates when canSubmit is true)
      onUserFeedInputBlur(event);

      expect(canSubmit.value).toBe(false);
    });
  });

  describe("form submission", () => {
    it("prevents default form submission", () => {
      const preventDefault = vi.fn();
      const formData = new Map([["userFeedUrl", "https://example.com/feed"]]);

      const event = {
        preventDefault,
        target: {
          reset: vi.fn(),
        },
      };

      // Mock FormData
      global.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      onUserFeedFormSubmit(event);
      expect(preventDefault).toHaveBeenCalled();
    });

    it("submits form with valid URL", () => {
      const url = "https://example.com/feed";
      const formData = new Map([["userFeedUrl", url]]);

      const event = {
        preventDefault: vi.fn(),
        target: {
          reset: vi.fn(),
        },
      };

      // Mock FormData
      global.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      onUserFeedFormSubmit(event);

      expect(event.target.reset).toHaveBeenCalled();
      expect(requestFeedFromURL).toHaveBeenCalledWith(url);
      expect(router.push).toHaveBeenCalledWith("/view");
    });

    it("does not submit form with invalid URL", () => {
      const url = "not-a-url";
      const formData = new Map([["userFeedUrl", url]]);

      const event = {
        preventDefault: vi.fn(),
        target: {
          reset: vi.fn(),
        },
      };

      // Mock FormData
      global.FormData = vi.fn(() => ({
        get: (key) => formData.get(key),
      }));

      onUserFeedFormSubmit(event);

      expect(event.target.reset).not.toHaveBeenCalled();
      expect(requestFeedFromURL).not.toHaveBeenCalled();
      expect(router.push).not.toHaveBeenCalled();
    });
  });

  describe("input events", () => {
    it("validates on blur", () => {
      // Initially canSubmit is true, so blur does nothing
      // We need to make it false first
      const invalidEvent = {
        target: { value: "not-a-url" },
      };
      onUserFeedInputInput(invalidEvent);

      // Now canSubmit is false, blur should validate
      const validEvent = {
        target: { value: "https://example.com/feed" },
      };
      onUserFeedInputBlur(validEvent);

      expect(canSubmit.value).toBe(true);
    });

    it("validates on input", () => {
      // First make it invalid
      onUserFeedInputInput({
        target: { value: "invalid" },
      });

      // Then make it valid
      const event = {
        target: { value: "https://example.com/feed" },
      };
      onUserFeedInputInput(event);

      expect(canSubmit.value).toBe(true);
    });
  });
});
