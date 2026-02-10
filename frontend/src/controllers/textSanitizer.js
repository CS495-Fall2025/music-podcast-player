import DOMPurify from "dompurify";

// Takes a string, a list of html tags, and a list of html attributes. Uses the two lists to properly sanitize the string, then returns the sanitized strings.
export function sanitizeText(
  rawText,
  allowedTags = ["p", "br", "a", "strong", "b", "em", "i", "ul", "ol", "li"],
  allowedAttr = ["href", "target"],
) {
  // If NO rawText OR if rawText is not a string, returns null.
  if (!rawText || typeof rawText !== "string") return null;

  // Otherwise, sanitize and return.
  return DOMPurify.sanitize(rawText, {
    ALLOWED_TAGS: allowedTags,
    ALLOWED_ATTR: allowedAttr,
  });
}
