import { describe, it, expect } from "vitest";
import { sanitizeText } from "../src/controllers/textSanitizer.js";

describe("sanitizeText()", () => {
  describe("Input Validation", () => {
    it("should return null if rawText is undefined or null", () => {
      expect(sanitizeText(undefined)).toBeNull();
      expect(sanitizeText(null)).toBeNull();
    });

    it("should return null if rawText is not a string", () => {
      expect(sanitizeText(123)).toBeNull();
      expect(sanitizeText({ text: "hello" })).toBeNull();
      expect(sanitizeText([])).toBeNull();
    });

    it("should return null if rawText is an empty string", () => {
      expect(sanitizeText("")).toBeNull();
    });
  });

  describe("Sanitization Logic", () => {
    it("should allow default tags and strip forbidden ones (like <script>)", () => {
      const input = "<div>Hello</div><p>World</p><script>alert('xss')</script>";
      const result = sanitizeText(input);

      // <div> is not in default allowedTags, <script> is dangerous
      expect(result).not.toContain("<script>");
      expect(result).not.toContain("<div>");
      expect(result).toContain("<p>World</p>");
    });

    it("should preserve default allowed attributes like 'href'", () => {
      const input = '<a href="https://google.com" onclick="steal()">Link</a>';
      const result = sanitizeText(input);

      expect(result).toContain('href="https://google.com"');
      expect(result).not.toContain("onclick");
    });

    it("should respect custom allowed tags and attributes", () => {
      const input = '<span title="hello">Custom Text</span>';
      const tags = ["span"];
      const attrs = ["title"];

      const result = sanitizeText(input, tags, attrs);

      expect(result).toBe('<span title="hello">Custom Text</span>');
    });

    it("should return a clean string when no HTML is present", () => {
      const input = "Just plain text";
      expect(sanitizeText(input)).toBe("Just plain text");
    });
  });
});
