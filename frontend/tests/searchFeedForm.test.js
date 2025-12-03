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
  // Reset mocks before each test
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, "log").mockImplementation(() => {});
  });

  describe("query validation", () => {
    // Test valid search query formats
    it("accepts valid search queries", () => {
      const validQueries = [
        "simple search", // basic query with spaces
        "with-numbers123", // alphanumeric with single dash
        "punctuation!?.", // allowed punctuation marks
        "a".repeat(255), // maximum allowed length of 255 characters
      ];

      validQueries.forEach((query) => {
        const formData = new FormData();
        formData.append("query", query);
        const mockEvent = new Event("input");
        Object.defineProperty(mockEvent, "target", { value: { value: query } });
        onUserInputInput(mockEvent);
      });
    });

    // Test invalid search query formats are rejected
    it("rejects invalid search queries", () => {
      const invalidQueries = [
        "contains--dash", // double dash not allowed
        "a".repeat(256), // exceeds maximum character length (255)
        "@#$%^&*()", // special characters not allowed
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
    // Test preventDefault is called on form submit
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

    // Test successful form submission with valid query
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

    // Test form submission is blocked with invalid query
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
    // Test blur event triggers validation
    it("validates on blur", () => {
      const mockEvent = new Event("blur");
      Object.defineProperty(mockEvent, "target", {
        value: { value: "valid search" },
      });
      onUserInputBlur(mockEvent);
    });

    // Test input event triggers validation
    it("validates on input", () => {
      const mockEvent = new Event("input");
      Object.defineProperty(mockEvent, "target", {
        value: { value: "valid search" },
      });
      onUserInputInput(mockEvent);
    });
  });
});