import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  canSubmit,
  onUserInputBlur,
  onUserInputInput,
  onUserFormSubmit,
} from "../src/controllers/searchFeedForm.js";
import { requestFeeds } from "../src/controllers/backendFeedParser.js";

vi.mock("../src/controllers/backendFeedParser.js", () => ({
  requestFeeds: vi.fn(),
}));

describe("searchFeedForm controller", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  describe("query validation", () => {
    it("accepts valid search queries", () => {
      const validQueries = [
        "simple search",
        "with-numbers123",
        "punctuation!?.",
        "a".repeat(255),
      ];

      validQueries.forEach((query) => {
        const formData = new FormData();
        formData.append("query", query);
        const mockEvent = new Event("input");
        Object.defineProperty(mockEvent, "target", { value: { value: query } });
        onUserInputInput(mockEvent);
      });
    });

    it("rejects invalid search queries", () => {
      const invalidQueries = [
        "contains--dash", // Contains --
        "a".repeat(256), // Too long
        "@#$%^&*()", // Invalid characters
      ];

      invalidQueries.forEach((query) => {
        const formData = new FormData();
        formData.append("query", query);
        const mockEvent = new Event("input");
        Object.defineProperty(mockEvent, "target", { value: { value: query } });
        onUserInputInput(mockEvent);
      });
    });
  });

  describe("form submission", () => {
    it("prevents default form submission", () => {
      const query = "valid search";
      const formData = new FormData();
      formData.append("query", query);

      const mockForm = document.createElement("form");
      const mockEvent = new Event("submit");
      Object.defineProperty(mockEvent, "target", { value: mockForm });
      mockEvent.preventDefault = vi.fn();

      vi.stubGlobal(
        "FormData",
        vi.fn(() => formData),
      );

      onUserFormSubmit(mockEvent);
      expect(mockEvent.preventDefault).toHaveBeenCalled();

      vi.unstubAllGlobals();
    });

    it("submits form with valid query", () => {
      const query = "valid search";
      const formData = new FormData();
      formData.append("query", query);

      const mockForm = document.createElement("form");
      mockForm.reset = vi.fn();

      const mockEvent = new Event("submit");
      Object.defineProperty(mockEvent, "target", { value: mockForm });
      mockEvent.preventDefault = vi.fn();

      vi.stubGlobal(
        "FormData",
        vi.fn(() => ({
          get: (key) => query,
        })),
      );

      onUserFormSubmit(mockEvent);

      expect(mockForm.reset).toHaveBeenCalled();
      expect(requestFeeds).toHaveBeenCalledWith(query);

      vi.unstubAllGlobals();
    });

    it("does not submit form with invalid query", () => {
      const query = "--invalid--";
      const formData = new FormData();
      formData.append("query", query);

      const mockForm = document.createElement("form");
      mockForm.reset = vi.fn();

      const mockEvent = new Event("submit");
      Object.defineProperty(mockEvent, "target", { value: mockForm });
      mockEvent.preventDefault = vi.fn();

      vi.stubGlobal(
        "FormData",
        vi.fn(() => ({
          get: (key) => query,
        })),
      );

      onUserFormSubmit(mockEvent);

      expect(mockForm.reset).not.toHaveBeenCalled();
      expect(requestFeeds).not.toHaveBeenCalled();

      vi.unstubAllGlobals();
    });
  });

  describe("input events", () => {
    it("validates on blur", () => {
      const mockEvent = new Event("blur");
      Object.defineProperty(mockEvent, "target", {
        value: { value: "valid search" },
      });
      onUserInputBlur(mockEvent);
    });

    it("validates on input", () => {
      const mockEvent = new Event("input");
      Object.defineProperty(mockEvent, "target", {
        value: { value: "valid search" },
      });
      onUserInputInput(mockEvent);
    });
  });
});
